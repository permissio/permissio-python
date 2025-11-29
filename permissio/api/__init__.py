"""
Permissio.io API clients.
"""

from permissio.api.base import BaseApiClient
from permissio.api.users import UsersApi
from permissio.api.tenants import TenantsApi
from permissio.api.roles import RolesApi
from permissio.api.resources import ResourcesApi
from permissio.api.role_assignments import RoleAssignmentsApi

__all__ = [
    "BaseApiClient",
    "UsersApi",
    "TenantsApi",
    "RolesApi",
    "ResourcesApi",
    "RoleAssignmentsApi",
]
