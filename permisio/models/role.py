"""
Role models for the Permis.io SDK.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime

from permisio.models.common import parse_datetime, format_datetime


@dataclass
class Role:
    """
    A role in the Permis.io system.

    Attributes:
        id: Unique role identifier.
        key: Role key.
        name: Role display name.
        description: Role description.
        permissions: List of permission keys.
        extends: List of role keys this role extends.
        attributes: Custom role attributes.
        created_at: When the role was created.
        updated_at: When the role was last updated.
    """

    id: str
    key: str
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    extends: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Role":
        """Create a Role from a dictionary."""
        return cls(
            id=data.get("id", ""),
            key=data.get("key", ""),
            name=data.get("name"),
            description=data.get("description"),
            permissions=data.get("permissions", []),
            extends=data.get("extends", []),
            attributes=data.get("attributes", {}),
            created_at=parse_datetime(data.get("created_at", data.get("createdAt"))),
            updated_at=parse_datetime(data.get("updated_at", data.get("updatedAt"))),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary."""
        return {
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions,
            "extends": self.extends,
            "attributes": self.attributes,
            "created_at": format_datetime(self.created_at),
            "updated_at": format_datetime(self.updated_at),
        }


@dataclass
class RoleCreate:
    """
    Data for creating a new role.

    Attributes:
        key: Role key.
        name: Role display name.
        description: Role description.
        permissions: List of permission keys.
        extends: List of role keys this role extends.
        attributes: Custom role attributes.
    """

    key: str
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    extends: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for API request."""
        data: Dict[str, Any] = {"key": self.key}
        if self.name is not None:
            data["name"] = self.name
        if self.description is not None:
            data["description"] = self.description
        if self.permissions:
            data["permissions"] = self.permissions
        if self.extends:
            data["extends"] = self.extends
        if self.attributes:
            data["attributes"] = self.attributes
        return data


@dataclass
class RoleUpdate:
    """
    Data for updating an existing role.

    Attributes:
        name: Role display name.
        description: Role description.
        permissions: List of permission keys.
        extends: List of role keys this role extends.
        attributes: Custom role attributes.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    extends: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for API request."""
        data: Dict[str, Any] = {}
        if self.name is not None:
            data["name"] = self.name
        if self.description is not None:
            data["description"] = self.description
        if self.permissions is not None:
            data["permissions"] = self.permissions
        if self.extends is not None:
            data["extends"] = self.extends
        if self.attributes is not None:
            data["attributes"] = self.attributes
        return data


@dataclass
class RoleRead:
    """
    Role data as returned from read operations (alias for Role).
    """

    id: str
    key: str
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    extends: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoleRead":
        """Create a RoleRead from a dictionary."""
        return cls(
            id=data.get("id", ""),
            key=data.get("key", ""),
            name=data.get("name"),
            description=data.get("description"),
            permissions=data.get("permissions", []),
            extends=data.get("extends", []),
            attributes=data.get("attributes", {}),
            created_at=parse_datetime(data.get("created_at", data.get("createdAt"))),
            updated_at=parse_datetime(data.get("updated_at", data.get("updatedAt"))),
        )
