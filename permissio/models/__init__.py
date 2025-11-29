"""
Permissio.io data models.
"""

from permissio.models.common import PaginatedResponse, Pagination
from permissio.models.user import User, UserCreate, UserUpdate, UserRead
from permissio.models.tenant import Tenant, TenantCreate, TenantUpdate, TenantRead
from permissio.models.role import Role, RoleCreate, RoleUpdate, RoleRead
from permissio.models.resource import Resource, ResourceCreate, ResourceUpdate, ResourceRead
from permissio.models.role_assignment import RoleAssignment, RoleAssignmentCreate, RoleAssignmentRead
from permissio.models.check import CheckRequest, CheckResponse

__all__ = [
    # Common
    "PaginatedResponse",
    "Pagination",
    # User
    "User",
    "UserCreate",
    "UserUpdate",
    "UserRead",
    # Tenant
    "Tenant",
    "TenantCreate",
    "TenantUpdate",
    "TenantRead",
    # Role
    "Role",
    "RoleCreate",
    "RoleUpdate",
    "RoleRead",
    # Resource
    "Resource",
    "ResourceCreate",
    "ResourceUpdate",
    "ResourceRead",
    # Role Assignment
    "RoleAssignment",
    "RoleAssignmentCreate",
    "RoleAssignmentRead",
    # Check
    "CheckRequest",
    "CheckResponse",
]
