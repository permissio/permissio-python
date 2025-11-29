"""
Permis.io data models.
"""

from permisio.models.common import PaginatedResponse, Pagination
from permisio.models.user import User, UserCreate, UserUpdate, UserRead
from permisio.models.tenant import Tenant, TenantCreate, TenantUpdate, TenantRead
from permisio.models.role import Role, RoleCreate, RoleUpdate, RoleRead
from permisio.models.resource import Resource, ResourceCreate, ResourceUpdate, ResourceRead
from permisio.models.role_assignment import RoleAssignment, RoleAssignmentCreate, RoleAssignmentRead
from permisio.models.check import CheckRequest, CheckResponse

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
