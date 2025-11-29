"""
Tenant models for the Permissio.io SDK.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

from permissio.models.common import parse_datetime, format_datetime


@dataclass
class Tenant:
    """
    A tenant in the Permissio.io system.

    Attributes:
        id: Unique tenant identifier.
        key: Tenant key.
        name: Tenant display name.
        description: Tenant description.
        attributes: Custom tenant attributes.
        created_at: When the tenant was created.
        updated_at: When the tenant was last updated.
    """

    id: str
    key: str
    name: Optional[str] = None
    description: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tenant":
        """Create a Tenant from a dictionary."""
        return cls(
            id=data.get("id", ""),
            key=data.get("key", ""),
            name=data.get("name"),
            description=data.get("description"),
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
            "attributes": self.attributes,
            "created_at": format_datetime(self.created_at),
            "updated_at": format_datetime(self.updated_at),
        }


@dataclass
class TenantCreate:
    """
    Data for creating a new tenant.

    Attributes:
        key: Tenant key.
        name: Tenant display name.
        description: Tenant description.
        attributes: Custom tenant attributes.
    """

    key: str
    name: Optional[str] = None
    description: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for API request."""
        data: Dict[str, Any] = {"key": self.key}
        if self.name is not None:
            data["name"] = self.name
        if self.description is not None:
            data["description"] = self.description
        if self.attributes:
            data["attributes"] = self.attributes
        return data


@dataclass
class TenantUpdate:
    """
    Data for updating an existing tenant.

    Attributes:
        name: Tenant display name.
        description: Tenant description.
        attributes: Custom tenant attributes.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for API request."""
        data: Dict[str, Any] = {}
        if self.name is not None:
            data["name"] = self.name
        if self.description is not None:
            data["description"] = self.description
        if self.attributes is not None:
            data["attributes"] = self.attributes
        return data


@dataclass
class TenantRead:
    """
    Tenant data as returned from read operations (alias for Tenant).
    """

    id: str
    key: str
    name: Optional[str] = None
    description: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TenantRead":
        """Create a TenantRead from a dictionary."""
        return cls(
            id=data.get("id", ""),
            key=data.get("key", ""),
            name=data.get("name"),
            description=data.get("description"),
            attributes=data.get("attributes", {}),
            created_at=parse_datetime(data.get("created_at", data.get("createdAt"))),
            updated_at=parse_datetime(data.get("updated_at", data.get("updatedAt"))),
        )
