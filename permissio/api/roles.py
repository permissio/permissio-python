"""
Roles API client for the Permissio.io SDK.
"""

from typing import Optional, Dict, Any, Union, List

from permissio.api.base import BaseApiClient
from permissio.config import PermissioConfig
from permissio.models.role import Role, RoleCreate, RoleUpdate, RoleRead
from permissio.models.common import PaginatedResponse


class RolesApi(BaseApiClient):
    """
    API client for role operations.

    Provides methods for creating, reading, updating, and deleting roles.
    Roles are part of the Schema API.
    """

    def __init__(self, config: PermissioConfig) -> None:
        """Initialize the Roles API client."""
        super().__init__(config)

    def list(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
    ) -> PaginatedResponse[RoleRead]:
        """
        List roles.

        Args:
            page: Page number (1-indexed).
            per_page: Number of items per page.
            search: Search query string.

        Returns:
            Paginated list of roles.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "include_total_count": "true",
        }
        if search:
            params["search"] = search

        url = self._build_schema_url("roles")
        response = self.request("GET", url, params=params)
        data = response.json()
        return PaginatedResponse.from_dict(data, RoleRead.from_dict)

    async def list_async(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
    ) -> PaginatedResponse[RoleRead]:
        """
        List roles (async).

        Args:
            page: Page number (1-indexed).
            per_page: Number of items per page.
            search: Search query string.

        Returns:
            Paginated list of roles.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "include_total_count": "true",
        }
        if search:
            params["search"] = search

        url = self._build_schema_url("roles")
        response = await self.request_async("GET", url, params=params)
        data = response.json()
        return PaginatedResponse.from_dict(data, RoleRead.from_dict)

    def get(self, role_key: str) -> RoleRead:
        """
        Get a role by key.

        Args:
            role_key: The role key.

        Returns:
            The role.
        """
        url = self._build_schema_url(f"roles/{role_key}")
        response = super().get(url)
        return RoleRead.from_dict(response.json())

    async def get_async(self, role_key: str) -> RoleRead:
        """
        Get a role by key (async).

        Args:
            role_key: The role key.

        Returns:
            The role.
        """
        url = self._build_schema_url(f"roles/{role_key}")
        response = await super().get_async(url)
        return RoleRead.from_dict(response.json())

    def create(self, role: Union[RoleCreate, Dict[str, Any]]) -> RoleRead:
        """
        Create a new role.

        Args:
            role: Role data.

        Returns:
            The created role.
        """
        if isinstance(role, RoleCreate):
            role_data = role.to_dict()
        else:
            role_data = role

        url = self._build_schema_url("roles")
        response = self.post(url, json=role_data)
        return RoleRead.from_dict(response.json())

    async def create_async(self, role: Union[RoleCreate, Dict[str, Any]]) -> RoleRead:
        """
        Create a new role (async).

        Args:
            role: Role data.

        Returns:
            The created role.
        """
        if isinstance(role, RoleCreate):
            role_data = role.to_dict()
        else:
            role_data = role

        url = self._build_schema_url("roles")
        response = await self.post_async(url, json=role_data)
        return RoleRead.from_dict(response.json())

    def update(self, role_key: str, role: Union[RoleUpdate, Dict[str, Any]]) -> RoleRead:
        """
        Update an existing role.

        Args:
            role_key: The role key.
            role: Role update data.

        Returns:
            The updated role.
        """
        if isinstance(role, RoleUpdate):
            role_data = role.to_dict()
        else:
            role_data = role

        url = self._build_schema_url(f"roles/{role_key}")
        response = self.patch(url, json=role_data)
        return RoleRead.from_dict(response.json())

    async def update_async(self, role_key: str, role: Union[RoleUpdate, Dict[str, Any]]) -> RoleRead:
        """
        Update an existing role (async).

        Args:
            role_key: The role key.
            role: Role update data.

        Returns:
            The updated role.
        """
        if isinstance(role, RoleUpdate):
            role_data = role.to_dict()
        else:
            role_data = role

        url = self._build_schema_url(f"roles/{role_key}")
        response = await self.patch_async(url, json=role_data)
        return RoleRead.from_dict(response.json())

    def delete(self, role_key: str) -> None:
        """
        Delete a role.

        Args:
            role_key: The role key.
        """
        url = self._build_schema_url(f"roles/{role_key}")
        super().delete(url)

    async def delete_async(self, role_key: str) -> None:
        """
        Delete a role (async).

        Args:
            role_key: The role key.
        """
        url = self._build_schema_url(f"roles/{role_key}")
        await super().delete_async(url)

    def add_permissions(self, role_key: str, permissions: List[str]) -> RoleRead:
        """
        Add permissions to a role.

        Args:
            role_key: The role key.
            permissions: List of permission keys to add.

        Returns:
            The updated role.
        """
        url = self._build_schema_url(f"roles/{role_key}/permissions")
        response = self.post(url, json={"permissions": permissions})
        return RoleRead.from_dict(response.json())

    async def add_permissions_async(self, role_key: str, permissions: List[str]) -> RoleRead:
        """
        Add permissions to a role (async).

        Args:
            role_key: The role key.
            permissions: List of permission keys to add.

        Returns:
            The updated role.
        """
        url = self._build_schema_url(f"roles/{role_key}/permissions")
        response = await self.post_async(url, json={"permissions": permissions})
        return RoleRead.from_dict(response.json())

    def remove_permissions(self, role_key: str, permissions: List[str]) -> RoleRead:
        """
        Remove permissions from a role.

        Args:
            role_key: The role key.
            permissions: List of permission keys to remove.

        Returns:
            The updated role.
        """
        url = self._build_schema_url(f"roles/{role_key}/permissions")
        response = self.request("DELETE", url, json={"permissions": permissions})
        return RoleRead.from_dict(response.json())

    async def remove_permissions_async(self, role_key: str, permissions: List[str]) -> RoleRead:
        """
        Remove permissions from a role (async).

        Args:
            role_key: The role key.
            permissions: List of permission keys to remove.

        Returns:
            The updated role.
        """
        url = self._build_schema_url(f"roles/{role_key}/permissions")
        response = await self.request_async("DELETE", url, json={"permissions": permissions})
        return RoleRead.from_dict(response.json())
