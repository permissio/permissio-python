"""
Resource models for the Permissio.io SDK.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime

from permissio.models.common import parse_datetime, format_datetime


@dataclass
class ResourceAction:
    """
    An action that can be performed on a resource.

    Attributes:
        key: Action key (e.g., 'read', 'write', 'delete').
        name: Action display name.
        description: Action description.
    """

    key: str
    name: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceAction":
        """Create a ResourceAction from a dictionary."""
        return cls(
            key=data.get("key", ""),
            name=data.get("name"),
            description=data.get("description"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary."""
        data: Dict[str, Any] = {"key": self.key}
        if self.name is not None:
            data["name"] = self.name
        if self.description is not None:
            data["description"] = self.description
        return data


@dataclass
class ResourceAttribute:
    """
    An attribute of a resource type.

    Attributes:
        key: Attribute key.
        type: Attribute data type (e.g., 'string', 'number', 'boolean').
        description: Attribute description.
    """

    key: str
    type: str = "string"
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceAttribute":
        """Create a ResourceAttribute from a dictionary."""
        return cls(
            key=data.get("key", ""),
            type=data.get("type", "string"),
            description=data.get("description"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary."""
        data: Dict[str, Any] = {"key": self.key, "type": self.type}
        if self.description is not None:
            data["description"] = self.description
        return data


@dataclass
class Resource:
    """
    A resource type in the Permissio.io system.

    Attributes:
        id: Unique resource identifier.
        key: Resource key.
        name: Resource display name.
        description: Resource description.
        actions: List of actions for this resource.
        attributes: List of attributes for this resource.
        urn: Resource URN pattern.
        created_at: When the resource was created.
        updated_at: When the resource was last updated.
    """

    id: str
    key: str
    name: Optional[str] = None
    description: Optional[str] = None
    actions: List[ResourceAction] = field(default_factory=list)
    attributes: List[ResourceAttribute] = field(default_factory=list)
    urn: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Resource":
        """Create a Resource from a dictionary."""
        actions = [ResourceAction.from_dict(a) for a in data.get("actions", [])]
        attributes = [ResourceAttribute.from_dict(a) for a in data.get("attributes", [])]
        return cls(
            id=data.get("id", ""),
            key=data.get("key", ""),
            name=data.get("name"),
            description=data.get("description"),
            actions=actions,
            attributes=attributes,
            urn=data.get("urn"),
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
            "actions": [a.to_dict() for a in self.actions],
            "attributes": [a.to_dict() for a in self.attributes],
            "urn": self.urn,
            "created_at": format_datetime(self.created_at),
            "updated_at": format_datetime(self.updated_at),
        }


@dataclass
class ResourceCreate:
    """
    Data for creating a new resource type.

    Attributes:
        key: Resource key.
        name: Resource display name.
        description: Resource description.
        actions: List of actions for this resource.
        attributes: List of attributes for this resource.
        urn: Resource URN pattern.
    """

    key: str
    name: Optional[str] = None
    description: Optional[str] = None
    actions: List[ResourceAction] = field(default_factory=list)
    attributes: List[ResourceAttribute] = field(default_factory=list)
    urn: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for API request."""
        data: Dict[str, Any] = {"key": self.key}
        if self.name is not None:
            data["name"] = self.name
        if self.description is not None:
            data["description"] = self.description
        if self.actions:
            data["actions"] = [a.to_dict() for a in self.actions]
        if self.attributes:
            data["attributes"] = [a.to_dict() for a in self.attributes]
        if self.urn is not None:
            data["urn"] = self.urn
        return data


@dataclass
class ResourceUpdate:
    """
    Data for updating an existing resource type.

    Attributes:
        name: Resource display name.
        description: Resource description.
        actions: List of actions for this resource.
        attributes: List of attributes for this resource.
        urn: Resource URN pattern.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    actions: Optional[List[ResourceAction]] = None
    attributes: Optional[List[ResourceAttribute]] = None
    urn: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for API request."""
        data: Dict[str, Any] = {}
        if self.name is not None:
            data["name"] = self.name
        if self.description is not None:
            data["description"] = self.description
        if self.actions is not None:
            data["actions"] = [a.to_dict() for a in self.actions]
        if self.attributes is not None:
            data["attributes"] = [a.to_dict() for a in self.attributes]
        if self.urn is not None:
            data["urn"] = self.urn
        return data


@dataclass
class ResourceRead:
    """
    Resource data as returned from read operations (alias for Resource).
    """

    id: str
    key: str
    name: Optional[str] = None
    description: Optional[str] = None
    actions: List[ResourceAction] = field(default_factory=list)
    attributes: List[ResourceAttribute] = field(default_factory=list)
    urn: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceRead":
        """Create a ResourceRead from a dictionary."""
        # Handle actions as either strings or objects
        raw_actions = data.get("actions", [])
        actions = []
        for a in raw_actions:
            if isinstance(a, str):
                actions.append(ResourceAction(key=a))
            elif isinstance(a, dict):
                actions.append(ResourceAction.from_dict(a))
        
        # Handle attributes as either strings or objects
        raw_attributes = data.get("attributes", [])
        attributes = []
        if isinstance(raw_attributes, list):
            for a in raw_attributes:
                if isinstance(a, str):
                    attributes.append(ResourceAttribute(key=a, type="string"))
                elif isinstance(a, dict):
                    attributes.append(ResourceAttribute.from_dict(a))
        
        return cls(
            id=data.get("id", ""),
            key=data.get("key", ""),
            name=data.get("name"),
            description=data.get("description"),
            actions=actions,
            attributes=attributes,
            urn=data.get("urn"),
            created_at=parse_datetime(data.get("created_at", data.get("createdAt"))),
            updated_at=parse_datetime(data.get("updated_at", data.get("updatedAt"))),
        )
