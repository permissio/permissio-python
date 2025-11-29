"""
Unit tests for the Permis.io Python SDK.

Run with: pytest tests/ -v
"""

import pytest
from permisio import Permis, PermisConfig, ConfigBuilder
from permisio.errors import (
    PermisError,
    PermisApiError,
    PermisValidationError,
    PermisAuthenticationError,
)
from permisio.enforcement import UserBuilder, ResourceBuilder, ContextBuilder


class TestConfig:
    """Tests for configuration."""
    
    def test_permis_config_defaults(self):
        config = PermisConfig(token="test_token")
        assert config.token == "test_token"
        assert config.api_url == "https://api.permis.io"
        assert config.project_id is None  # Default is None, set during ConfigBuilder
        assert config.environment_id is None
        assert config.timeout == 30.0
        assert config.debug is False
    
    def test_permis_config_custom_values(self):
        config = PermisConfig(
            token="test_token",
            api_url="http://localhost:8080",
            project_id="my-project",
            environment_id="production",
            timeout=60.0,
            debug=True,
        )
        assert config.api_url == "http://localhost:8080"
        assert config.project_id == "my-project"
        assert config.environment_id == "production"
        assert config.timeout == 60.0
        assert config.debug is True
    
    def test_config_builder(self):
        config = (
            ConfigBuilder("test_token")
            .with_api_url("http://localhost:8080")
            .with_project_id("my-project")
            .with_environment_id("staging")
            .with_timeout(45.0)
            .with_debug(True)
            .with_retry_attempts(5)
            .with_throw_on_error(False)
            .build()
        )
        
        assert config.token == "test_token"
        assert config.api_url == "http://localhost:8080"
        assert config.project_id == "my-project"
        assert config.environment_id == "staging"
        assert config.timeout == 45.0
        assert config.debug is True
        assert config.retry_attempts == 5
        assert config.throw_on_error is False
    
    def test_config_builder_with_custom_headers(self):
        config = (
            ConfigBuilder("test_token")
            .with_custom_header("X-Custom", "value")
            .with_custom_header("X-Another", "another")
            .build()
        )
        
        assert config.custom_headers == {"X-Custom": "value", "X-Another": "another"}


class TestClient:
    """Tests for client initialization."""
    
    def test_client_init_with_token(self):
        client = Permis(token="test_token")
        assert client.config.token == "test_token"
        client.close()
    
    def test_client_init_with_config(self):
        config = PermisConfig(
            token="test_token",
            project_id="my-project",
        )
        client = Permis(config=config)
        assert client.config.project_id == "my-project"
        client.close()
    
    def test_client_init_with_kwargs(self):
        client = Permis(
            token="test_token",
            project_id="custom-project",
            environment_id="production",
        )
        assert client.config.project_id == "custom-project"
        assert client.config.environment_id == "production"
        client.close()
    
    def test_client_requires_token(self):
        with pytest.raises(ValueError):  # Raises ValueError, not PermisValidationError
            Permis()
    
    def test_client_api_property(self):
        client = Permis(token="test_token")
        assert client.api is not None
        assert client.api.users is not None
        assert client.api.tenants is not None
        assert client.api.roles is not None
        assert client.api.resources is not None
        assert client.api.role_assignments is not None
        client.close()


class TestEnforcementBuilders:
    """Tests for enforcement builders."""
    
    def test_user_builder_simple(self):
        user = UserBuilder("user@example.com").build()
        assert user.key == "user@example.com"
        assert user.attributes == {}
    
    def test_user_builder_with_attributes(self):
        user = (
            UserBuilder("user@example.com")
            .with_attribute("department", "engineering")
            .with_attribute("level", 5)
            .with_attributes({"location": "US", "team": "platform"})
            .build()
        )
        
        assert user.key == "user@example.com"
        assert user.attributes["department"] == "engineering"
        assert user.attributes["level"] == 5
        assert user.attributes["location"] == "US"
        assert user.attributes["team"] == "platform"
    
    def test_resource_builder_simple(self):
        resource = ResourceBuilder("document").build()
        assert resource.type == "document"
        assert resource.key is None
        assert resource.tenant is None
    
    def test_resource_builder_with_all_options(self):
        resource = (
            ResourceBuilder("document")
            .with_key("doc-123")
            .with_tenant("acme-corp")
            .with_attribute("classification", "confidential")
            .with_attribute("owner", "user@example.com")
            .build()
        )
        
        assert resource.type == "document"
        assert resource.key == "doc-123"
        assert resource.tenant == "acme-corp"
        assert resource.attributes["classification"] == "confidential"
        assert resource.attributes["owner"] == "user@example.com"
    
    def test_context_builder(self):
        context = (
            ContextBuilder()
            .with_value("ip_address", "192.168.1.1")
            .with_value("time_of_day", "business_hours")
            .with_values({"request_id": "abc123"})
            .build()
        )
        
        # CheckContext uses 'data' attribute, not 'values'
        assert context.data["ip_address"] == "192.168.1.1"
        assert context.data["time_of_day"] == "business_hours"
        assert context.data["request_id"] == "abc123"


class TestErrors:
    """Tests for error handling."""
    
    def test_permis_error_hierarchy(self):
        assert issubclass(PermisApiError, PermisError)
        assert issubclass(PermisValidationError, PermisError)
        assert issubclass(PermisAuthenticationError, PermisApiError)
    
    def test_permis_api_error(self):
        # PermisApiError uses 'code' not 'error_code'
        error = PermisApiError(
            message="Not found",
            status_code=404,
            code="RESOURCE_NOT_FOUND",
        )
        
        assert error.message == "Not found"
        assert error.status_code == 404
        assert error.code == "RESOURCE_NOT_FOUND"
        assert "Not found" in str(error)
    
    def test_permis_validation_error(self):
        error = PermisValidationError(
            message="Invalid input",
            field="email",
        )
        
        assert error.message == "Invalid input"
        assert error.field == "email"


class TestModels:
    """Tests for data models."""
    
    def test_user_create(self):
        from permisio.models import UserCreate
        
        user = UserCreate(
            key="user@example.com",
            email="user@example.com",
            first_name="John",
            last_name="Doe",
            attributes={"department": "sales"},
        )
        
        assert user.key == "user@example.com"
        assert user.email == "user@example.com"
        assert user.first_name == "John"
        assert user.attributes["department"] == "sales"
    
    def test_tenant_create(self):
        from permisio.models import TenantCreate
        
        tenant = TenantCreate(
            key="acme-corp",
            name="Acme Corporation",
            description="A test tenant",
        )
        
        assert tenant.key == "acme-corp"
        assert tenant.name == "Acme Corporation"
    
    def test_role_create(self):
        from permisio.models import RoleCreate
        
        role = RoleCreate(
            key="editor",
            name="Editor",
            permissions=["read", "write"],
        )
        
        assert role.key == "editor"
        assert "read" in role.permissions


class TestNormalizeFunctions:
    """Tests for input normalization."""
    
    def test_normalize_user_string(self):
        from permisio.enforcement.models import normalize_user
        
        # normalize_user returns a dict, not CheckUser
        result = normalize_user("user@example.com")
        assert result["key"] == "user@example.com"
    
    def test_normalize_user_dict(self):
        from permisio.enforcement.models import normalize_user
        
        result = normalize_user({
            "key": "user@example.com",
            "attributes": {"level": 5},
        })
        assert result["key"] == "user@example.com"
        assert result["attributes"]["level"] == 5
    
    def test_normalize_user_object(self):
        from permisio.enforcement.models import normalize_user, CheckUser
        
        user = CheckUser(key="user@example.com", attributes={})
        result = normalize_user(user)
        # Returns a dict representation, not the same object
        assert result["key"] == "user@example.com"
    
    def test_normalize_resource_string(self):
        from permisio.enforcement.models import normalize_resource
        
        result = normalize_resource("document")
        assert result["type"] == "document"
    
    def test_normalize_resource_dict(self):
        from permisio.enforcement.models import normalize_resource
        
        result = normalize_resource({
            "type": "document",
            "key": "doc-123",
            "tenant": "acme",
        })
        assert result["type"] == "document"
        assert result["key"] == "doc-123"
        assert result["tenant"] == "acme"
