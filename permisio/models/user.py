"""
User models for the Permis.io SDK.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime

from permisio.models.common import parse_datetime, format_datetime


@dataclass
class User:
    """
    A user in the Permis.io system.

    Attributes:
        id: Unique user identifier.
        key: User key (often email or external ID).
        email: User email address.
        first_name: User's first name.
        last_name: User's last name.
        attributes: Custom user attributes.
        created_at: When the user was created.
        updated_at: When the user was last updated.
    """

    id: str
    key: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create a User from a dictionary."""
        return cls(
            id=data.get("id", ""),
            key=data.get("key", ""),
            email=data.get("email"),
            first_name=data.get("first_name", data.get("firstName")),
            last_name=data.get("last_name", data.get("lastName")),
            attributes=data.get("attributes", {}),
            created_at=parse_datetime(data.get("created_at", data.get("createdAt"))),
            updated_at=parse_datetime(data.get("updated_at", data.get("updatedAt"))),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary."""
        return {
            "id": self.id,
            "key": self.key,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "attributes": self.attributes,
            "created_at": format_datetime(self.created_at),
            "updated_at": format_datetime(self.updated_at),
        }


@dataclass
class UserCreate:
    """
    Data for creating a new user.

    Attributes:
        key: User key (often email or external ID).
        email: User email address.
        first_name: User's first name.
        last_name: User's last name.
        attributes: Custom user attributes.
    """

    key: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for API request."""
        data: Dict[str, Any] = {"key": self.key}
        if self.email is not None:
            data["email"] = self.email
        if self.first_name is not None:
            data["first_name"] = self.first_name
        if self.last_name is not None:
            data["last_name"] = self.last_name
        if self.attributes:
            data["attributes"] = self.attributes
        return data


@dataclass
class UserUpdate:
    """
    Data for updating an existing user.

    Attributes:
        email: User email address.
        first_name: User's first name.
        last_name: User's last name.
        attributes: Custom user attributes.
    """

    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for API request."""
        data: Dict[str, Any] = {}
        if self.email is not None:
            data["email"] = self.email
        if self.first_name is not None:
            data["first_name"] = self.first_name
        if self.last_name is not None:
            data["last_name"] = self.last_name
        if self.attributes is not None:
            data["attributes"] = self.attributes
        return data


@dataclass
class UserRead:
    """
    User data as returned from read operations (alias for User).
    """

    id: str
    key: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserRead":
        """Create a UserRead from a dictionary."""
        return cls(
            id=data.get("id", ""),
            key=data.get("key", ""),
            email=data.get("email"),
            first_name=data.get("first_name", data.get("firstName")),
            last_name=data.get("last_name", data.get("lastName")),
            attributes=data.get("attributes", {}),
            created_at=parse_datetime(data.get("created_at", data.get("createdAt"))),
            updated_at=parse_datetime(data.get("updated_at", data.get("updatedAt"))),
        )


@dataclass
class UserRole:
    """
    A role assigned to a user.

    Attributes:
        role: Role key.
        tenant: Tenant key.
        resource_instance: Resource instance key (optional).
    """

    role: str
    tenant: Optional[str] = None
    resource_instance: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserRole":
        """Create a UserRole from a dictionary."""
        return cls(
            role=data.get("role", ""),
            tenant=data.get("tenant"),
            resource_instance=data.get("resource_instance", data.get("resourceInstance")),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary."""
        data: Dict[str, Any] = {"role": self.role}
        if self.tenant is not None:
            data["tenant"] = self.tenant
        if self.resource_instance is not None:
            data["resource_instance"] = self.resource_instance
        return data


@dataclass
class UserSync:
    """
    Data for syncing a user with roles.

    Attributes:
        key: User key.
        email: User email address.
        first_name: User's first name.
        last_name: User's last name.
        attributes: Custom user attributes.
        roles: List of roles to assign.
    """

    key: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    roles: List[UserRole] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for API request."""
        data: Dict[str, Any] = {"key": self.key}
        if self.email is not None:
            data["email"] = self.email
        if self.first_name is not None:
            data["first_name"] = self.first_name
        if self.last_name is not None:
            data["last_name"] = self.last_name
        if self.attributes:
            data["attributes"] = self.attributes
        if self.roles:
            data["roles"] = [r.to_dict() for r in self.roles]
        return data
