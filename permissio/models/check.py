"""
Permission check models for the Permissio.io SDK.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class CheckRequest:
    """
    Request for a permission check.

    Attributes:
        user: User identifier (key or full user object).
        action: Action to check permission for.
        resource: Resource to check permission on (type or full resource object).
        tenant: Tenant identifier (optional).
        context: Additional context for the check (optional).
    """

    user: Union[str, Dict[str, Any]]
    action: str
    resource: Union[str, Dict[str, Any]]
    tenant: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for API request."""
        # Normalize user
        if isinstance(self.user, str):
            user_data = {"key": self.user}
        else:
            user_data = self.user

        # Normalize resource
        if isinstance(self.resource, str):
            resource_data = {"type": self.resource}
        else:
            resource_data = self.resource

        data: Dict[str, Any] = {
            "user": user_data,
            "action": self.action,
            "resource": resource_data,
        }

        if self.tenant is not None:
            data["tenant"] = self.tenant
        if self.context:
            data["context"] = self.context

        return data


@dataclass
class CheckResponse:
    """
    Response from a permission check.

    Attributes:
        allowed: Whether the action is allowed.
        user: User information from the check.
        action: Action that was checked.
        resource: Resource that was checked.
        tenant: Tenant that was checked (if applicable).
        reason: Reason for the decision (optional).
        matched_roles: List of roles that granted the permission (optional).
        debug: Debug information (optional).
    """

    allowed: bool
    user: Optional[Dict[str, Any]] = None
    action: Optional[str] = None
    resource: Optional[Dict[str, Any]] = None
    tenant: Optional[str] = None
    reason: Optional[str] = None
    matched_roles: Optional[List[str]] = None
    debug: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CheckResponse":
        """Create a CheckResponse from a dictionary."""
        return cls(
            allowed=data.get("allowed", False),
            user=data.get("user"),
            action=data.get("action"),
            resource=data.get("resource"),
            tenant=data.get("tenant"),
            reason=data.get("reason"),
            matched_roles=data.get("matched_roles"),
            debug=data.get("debug"),
        )

    def __bool__(self) -> bool:
        """Allow using the response directly in boolean context."""
        return self.allowed


@dataclass
class BulkCheckRequest:
    """
    Request for bulk permission checks.

    Attributes:
        checks: List of check requests.
    """

    checks: list = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for API request."""
        return {
            "checks": [c.to_dict() if hasattr(c, "to_dict") else c for c in self.checks]
        }


@dataclass
class BulkCheckResponse:
    """
    Response from bulk permission checks.

    Attributes:
        results: List of check responses.
    """

    results: list = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BulkCheckResponse":
        """Create a BulkCheckResponse from a dictionary."""
        results = [CheckResponse.from_dict(r) for r in data.get("results", [])]
        return cls(results=results)

    def all_allowed(self) -> bool:
        """Check if all permissions are allowed."""
        return all(r.allowed for r in self.results)

    def any_allowed(self) -> bool:
        """Check if any permission is allowed."""
        return any(r.allowed for r in self.results)
