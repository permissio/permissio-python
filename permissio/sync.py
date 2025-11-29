"""
Synchronous wrapper for the Permissio.io SDK.

This module provides a synchronous-first interface similar to Permit.io's SDK.
Use this when you prefer synchronous API calls.

Example:
    from permissio.sync import Permissio

    permissio = Permissio(
        token="permis_key_your_api_key",
        project_id="my-project",
        environment_id="production",
    )

    # Check permission (synchronous)
    if permissio.check("user@example.com", "read", "document"):
        print("Access granted")
"""

# Re-export the main Permissio class for convenience
# The Permissio class already provides both sync and async methods
from permissio.client import Permissio, PermissioApi
from permissio.config import PermissioConfig, ConfigBuilder
from permissio.errors import (
    PermissioError,
    PermissioApiError,
    PermissioValidationError,
    PermissioNetworkError,
    PermissioTimeoutError,
    PermissioRateLimitError,
    PermissioAuthenticationError,
    PermissioPermissionError,
    PermissioNotFoundError,
    PermissioConflictError,
)
from permissio.enforcement import (
    UserBuilder,
    ResourceBuilder,
    CheckUser,
    CheckResource,
    CheckContext,
)
from permissio.models import (
    User,
    UserCreate,
    UserUpdate,
    Tenant,
    TenantCreate,
    TenantUpdate,
    Role,
    RoleCreate,
    RoleUpdate,
    Resource,
    ResourceCreate,
    ResourceUpdate,
    RoleAssignment,
    RoleAssignmentCreate,
    CheckRequest,
    CheckResponse,
)

__all__ = [
    # Main client
    "Permissio",
    "PermissioApi",
    # Config
    "PermissioConfig",
    "ConfigBuilder",
    # Errors
    "PermissioError",
    "PermissioApiError",
    "PermissioValidationError",
    "PermissioNetworkError",
    "PermissioTimeoutError",
    "PermissioRateLimitError",
    "PermissioAuthenticationError",
    "PermissioPermissionError",
    "PermissioNotFoundError",
    "PermissioConflictError",
    # Enforcement
    "UserBuilder",
    "ResourceBuilder",
    "CheckUser",
    "CheckResource",
    "CheckContext",
    # Models
    "User",
    "UserCreate",
    "UserUpdate",
    "Tenant",
    "TenantCreate",
    "TenantUpdate",
    "Role",
    "RoleCreate",
    "RoleUpdate",
    "Resource",
    "ResourceCreate",
    "ResourceUpdate",
    "RoleAssignment",
    "RoleAssignmentCreate",
    "CheckRequest",
    "CheckResponse",
]
