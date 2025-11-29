"""
Permis.io API clients.
"""

from permisio.api.base import BaseApiClient
from permisio.api.users import UsersApi
from permisio.api.tenants import TenantsApi
from permisio.api.roles import RolesApi
from permisio.api.resources import ResourcesApi
from permisio.api.role_assignments import RoleAssignmentsApi

__all__ = [
    "BaseApiClient",
    "UsersApi",
    "TenantsApi",
    "RolesApi",
    "ResourcesApi",
    "RoleAssignmentsApi",
]
