"""
Enforcement models for permission checks in the Permissio.io SDK.

This module provides builder patterns for constructing permission check requests
with support for ABAC (Attribute-Based Access Control).
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union


@dataclass
class CheckUser:
    """
    User representation for permission checks.

    Attributes:
        key: User identifier (user key or ID).
        attributes: User attributes for ABAC.
        first_name: User's first name.
        last_name: User's last name.
        email: User's email.
    """

    key: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        data: Dict[str, Any] = {"key": self.key}
        if self.attributes:
            data["attributes"] = self.attributes
        if self.first_name is not None:
            data["first_name"] = self.first_name
        if self.last_name is not None:
            data["last_name"] = self.last_name
        if self.email is not None:
            data["email"] = self.email
        return data


@dataclass
class CheckResource:
    """
    Resource representation for permission checks.

    Attributes:
        type: Resource type key.
        key: Resource instance key (optional).
        tenant: Tenant key (optional).
        attributes: Resource attributes for ABAC.
    """

    type: str
    key: Optional[str] = None
    tenant: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        data: Dict[str, Any] = {"type": self.type}
        if self.key is not None:
            data["key"] = self.key
        if self.tenant is not None:
            data["tenant"] = self.tenant
        if self.attributes:
            data["attributes"] = self.attributes
        return data


@dataclass
class CheckContext:
    """
    Additional context for permission checks.

    Attributes:
        data: Arbitrary context data.
    """

    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        return self.data.copy()


class UserBuilder:
    """
    Builder for constructing CheckUser instances.

    Example:
        user = (
            UserBuilder("user@example.com")
            .with_attribute("department", "engineering")
            .with_attribute("level", 5)
            .with_first_name("John")
            .with_last_name("Doe")
            .build()
        )
    """

    def __init__(self, key: str) -> None:
        """
        Initialize the user builder.

        Args:
            key: User identifier (key or ID).
        """
        self._key = key
        self._attributes: Dict[str, Any] = {}
        self._first_name: Optional[str] = None
        self._last_name: Optional[str] = None
        self._email: Optional[str] = None

    def with_attribute(self, key: str, value: Any) -> "UserBuilder":
        """Add a user attribute."""
        self._attributes[key] = value
        return self

    def with_attributes(self, attributes: Dict[str, Any]) -> "UserBuilder":
        """Add multiple user attributes."""
        self._attributes.update(attributes)
        return self

    def with_first_name(self, first_name: str) -> "UserBuilder":
        """Set the user's first name."""
        self._first_name = first_name
        return self

    def with_last_name(self, last_name: str) -> "UserBuilder":
        """Set the user's last name."""
        self._last_name = last_name
        return self

    def with_email(self, email: str) -> "UserBuilder":
        """Set the user's email."""
        self._email = email
        return self

    def build(self) -> CheckUser:
        """Build the CheckUser instance."""
        return CheckUser(
            key=self._key,
            attributes=self._attributes.copy(),
            first_name=self._first_name,
            last_name=self._last_name,
            email=self._email,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert directly to dictionary without building."""
        return self.build().to_dict()


class ResourceBuilder:
    """
    Builder for constructing CheckResource instances.

    Example:
        resource = (
            ResourceBuilder("document")
            .with_key("doc-123")
            .with_tenant("acme-corp")
            .with_attribute("classification", "confidential")
            .build()
        )
    """

    def __init__(self, resource_type: str) -> None:
        """
        Initialize the resource builder.

        Args:
            resource_type: The resource type key.
        """
        self._type = resource_type
        self._key: Optional[str] = None
        self._tenant: Optional[str] = None
        self._attributes: Dict[str, Any] = {}

    def with_key(self, key: str) -> "ResourceBuilder":
        """Set the resource instance key."""
        self._key = key
        return self

    def with_tenant(self, tenant: str) -> "ResourceBuilder":
        """Set the tenant key."""
        self._tenant = tenant
        return self

    def with_attribute(self, key: str, value: Any) -> "ResourceBuilder":
        """Add a resource attribute."""
        self._attributes[key] = value
        return self

    def with_attributes(self, attributes: Dict[str, Any]) -> "ResourceBuilder":
        """Add multiple resource attributes."""
        self._attributes.update(attributes)
        return self

    def build(self) -> CheckResource:
        """Build the CheckResource instance."""
        return CheckResource(
            type=self._type,
            key=self._key,
            tenant=self._tenant,
            attributes=self._attributes.copy(),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert directly to dictionary without building."""
        return self.build().to_dict()


class ContextBuilder:
    """
    Builder for constructing CheckContext instances.

    Example:
        context = (
            ContextBuilder()
            .with_value("ip_address", "192.168.1.1")
            .with_value("request_time", "2024-01-01T12:00:00Z")
            .build()
        )
    """

    def __init__(self) -> None:
        """Initialize the context builder."""
        self._data: Dict[str, Any] = {}

    def with_value(self, key: str, value: Any) -> "ContextBuilder":
        """Add a context value."""
        self._data[key] = value
        return self

    def with_values(self, values: Dict[str, Any]) -> "ContextBuilder":
        """Add multiple context values."""
        self._data.update(values)
        return self

    def build(self) -> CheckContext:
        """Build the CheckContext instance."""
        return CheckContext(data=self._data.copy())

    def to_dict(self) -> Dict[str, Any]:
        """Convert directly to dictionary without building."""
        return self.build().to_dict()


def normalize_user(user: Union[str, Dict[str, Any], CheckUser, UserBuilder]) -> Dict[str, Any]:
    """
    Normalize a user input to a dictionary.

    Args:
        user: User as string (key), dict, CheckUser, or UserBuilder.

    Returns:
        Dictionary representation of the user.
    """
    if isinstance(user, str):
        return {"key": user}
    elif isinstance(user, CheckUser):
        return user.to_dict()
    elif isinstance(user, UserBuilder):
        return user.to_dict()
    elif isinstance(user, dict):
        # Ensure 'key' is present
        if "key" not in user and "userId" in user:
            user = user.copy()
            user["key"] = user.pop("userId")
        return user
    else:
        raise ValueError(f"Invalid user type: {type(user)}")


def normalize_resource(resource: Union[str, Dict[str, Any], CheckResource, ResourceBuilder]) -> Dict[str, Any]:
    """
    Normalize a resource input to a dictionary.

    Args:
        resource: Resource as string (type), dict, CheckResource, or ResourceBuilder.

    Returns:
        Dictionary representation of the resource.
    """
    if isinstance(resource, str):
        return {"type": resource}
    elif isinstance(resource, CheckResource):
        return resource.to_dict()
    elif isinstance(resource, ResourceBuilder):
        return resource.to_dict()
    elif isinstance(resource, dict):
        return resource
    else:
        raise ValueError(f"Invalid resource type: {type(resource)}")


def normalize_context(context: Optional[Union[Dict[str, Any], CheckContext, ContextBuilder]]) -> Dict[str, Any]:
    """
    Normalize a context input to a dictionary.

    Args:
        context: Context as dict, CheckContext, ContextBuilder, or None.

    Returns:
        Dictionary representation of the context.
    """
    if context is None:
        return {}
    elif isinstance(context, CheckContext):
        return context.to_dict()
    elif isinstance(context, ContextBuilder):
        return context.to_dict()
    elif isinstance(context, dict):
        return context
    else:
        raise ValueError(f"Invalid context type: {type(context)}")
