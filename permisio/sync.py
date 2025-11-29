"""
Synchronous wrapper for the Permis.io SDK.

This module provides a synchronous-first interface similar to Permit.io's SDK.
Use this when you prefer synchronous API calls.

Example:
    from permisio.sync import Permis

    permis = Permis(
        token="permis_key_your_api_key",
        project_id="my-project",
        environment_id="production",
    )

    # Check permission (synchronous)
    if permis.check("user@example.com", "read", "document"):
        print("Access granted")
"""

# Re-export the main Permis class for convenience
# The Permis class already provides both sync and async methods
from permisio.client import Permis, PermisApi
from permisio.config import PermisConfig, ConfigBuilder
from permisio.errors import (
    PermisError,
    PermisApiError,
    PermisValidationError,
    PermisNetworkError,
    PermisTimeoutError,
    PermisRateLimitError,
    PermisAuthenticationError,
    PermisPermissionError,
    PermisNotFoundError,
    PermisConflictError,
)
from permisio.enforcement import (
    UserBuilder,
    ResourceBuilder,
    CheckUser,
    CheckResource,
    CheckContext,
)
from permisio.models import (
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
    "Permis",
    "PermisApi",
    # Config
    "PermisConfig",
    "ConfigBuilder",
    # Errors
    "PermisError",
    "PermisApiError",
    "PermisValidationError",
    "PermisNetworkError",
    "PermisTimeoutError",
    "PermisRateLimitError",
    "PermisAuthenticationError",
    "PermisPermissionError",
    "PermisNotFoundError",
    "PermisConflictError",
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
