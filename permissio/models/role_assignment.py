"""
Role assignment models for the Permissio.io SDK.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

from permissio.models.common import parse_datetime, format_datetime


@dataclass
class RoleAssignment:
    """
    A role assignment in the Permissio.io system.

    Attributes:
        id: Unique role assignment identifier.
        user: User key.
        role: Role key.
        tenant: Tenant key (optional).
        user_id: User ID (optional).
        role_id: Role ID (optional).
        tenant_id: Tenant ID (optional).
        resource_instance: Resource instance key (optional).
        created_at: When the assignment was created.
    """

    id: str
    user: str
    role: str
    tenant: Optional[str] = None
    user_id: Optional[str] = None
    role_id: Optional[str] = None
    tenant_id: Optional[str] = None
    resource_instance: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoleAssignment":
        """Create a RoleAssignment from a dictionary."""
        return cls(
            id=data.get("id", ""),
            user=data.get("user", data.get("user_key", data.get("userKey", ""))),
            role=data.get("role", data.get("role_key", data.get("roleKey", ""))),
            tenant=data.get("tenant", data.get("tenant_key", data.get("tenantKey"))),
            user_id=data.get("user_id", data.get("userId")),
            role_id=data.get("role_id", data.get("roleId")),
            tenant_id=data.get("tenant_id", data.get("tenantId")),
            resource_instance=data.get("resource_instance", data.get("resourceInstance")),
            created_at=parse_datetime(data.get("created_at", data.get("createdAt"))),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary."""
        return {
            "id": self.id,
            "user": self.user,
            "role": self.role,
            "tenant": self.tenant,
            "user_id": self.user_id,
            "role_id": self.role_id,
            "tenant_id": self.tenant_id,
            "resource_instance": self.resource_instance,
            "created_at": format_datetime(self.created_at),
        }


@dataclass
class RoleAssignmentCreate:
    """
    Data for creating a new role assignment.

    Attributes:
        user: User key or ID.
        role: Role key or ID.
        tenant: Tenant key or ID (optional).
        resource_instance: Resource instance key (optional).
    """

    user: str
    role: str
    tenant: Optional[str] = None
    resource_instance: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for API request."""
        data: Dict[str, Any] = {
            "user": self.user,
            "role": self.role,
        }
        if self.tenant is not None:
            data["tenant"] = self.tenant
        if self.resource_instance is not None:
            data["resource_instance"] = self.resource_instance
        return data


@dataclass
class RoleAssignmentRead:
    """
    Role assignment data as returned from read operations.
    """

    id: str
    user_id: str
    user_key: str
    role_id: str
    role_key: str
    tenant_id: Optional[str] = None
    tenant_key: Optional[str] = None
    resource_instance: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoleAssignmentRead":
        """Create a RoleAssignmentRead from a dictionary."""
        return cls(
            id=data.get("id", ""),
            user_id=data.get("user_id", data.get("userId", "")),
            user_key=data.get("user_key", data.get("userKey", "")),
            role_id=data.get("role_id", data.get("roleId", "")),
            role_key=data.get("role_key", data.get("roleKey", "")),
            tenant_id=data.get("tenant_id", data.get("tenantId")),
            tenant_key=data.get("tenant_key", data.get("tenantKey")),
            resource_instance=data.get("resource_instance", data.get("resourceInstance")),
            created_at=parse_datetime(data.get("created_at", data.get("createdAt"))),
        )


@dataclass
class BulkRoleAssignment:
    """
    Data for bulk role assignment operations.

    Attributes:
        assignments: List of role assignments to create.
    """

    assignments: list = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for API request."""
        return {
            "assignments": [a.to_dict() if hasattr(a, "to_dict") else a for a in self.assignments]
        }
