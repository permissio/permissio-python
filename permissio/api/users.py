"""
Users API client for the Permissio.io SDK.
"""

from typing import Any, Dict, List, Optional, Union

from permissio.api.base import BaseApiClient
from permissio.config import PermissioConfig
from permissio.models.common import PaginatedResponse
from permissio.models.role_assignment import RoleAssignment, RoleAssignmentCreate
from permissio.models.user import UserCreate, UserRead, UserSync, UserUpdate


class UsersApi(BaseApiClient):
    """
    API client for user operations.

    Provides methods for creating, reading, updating, and deleting users,
    as well as managing user role assignments.
    """

    def __init__(self, config: PermissioConfig) -> None:
        """Initialize the Users API client."""
        super().__init__(config)

    def list(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        tenant: Optional[str] = None,
    ) -> PaginatedResponse[UserRead]:
        """
        List users.

        Args:
            page: Page number (1-indexed).
            per_page: Number of items per page.
            search: Search query string.
            tenant: Filter by tenant key.

        Returns:
            Paginated list of users.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "include_total_count": "true",
        }
        if search:
            params["search"] = search
        if tenant:
            params["tenant"] = tenant

        url = self._build_facts_url("users")
        response = self.request("GET", url, params=params)
        data = response.json()
        return PaginatedResponse.from_dict(data, UserRead.from_dict)

    async def list_async(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        tenant: Optional[str] = None,
    ) -> PaginatedResponse[UserRead]:
        """
        List users (async).

        Args:
            page: Page number (1-indexed).
            per_page: Number of items per page.
            search: Search query string.
            tenant: Filter by tenant key.

        Returns:
            Paginated list of users.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "include_total_count": "true",
        }
        if search:
            params["search"] = search
        if tenant:
            params["tenant"] = tenant

        url = self._build_facts_url("users")
        response = await self.request_async("GET", url, params=params)
        data = response.json()
        return PaginatedResponse.from_dict(data, UserRead.from_dict)

    def get(self, user_key: str) -> UserRead:
        """
        Get a user by key.

        Args:
            user_key: The user key.

        Returns:
            The user.
        """
        url = self._build_facts_url(f"users/{user_key}")
        response = super().get(url)
        return UserRead.from_dict(response.json())

    async def get_async(self, user_key: str) -> UserRead:
        """
        Get a user by key (async).

        Args:
            user_key: The user key.

        Returns:
            The user.
        """
        url = self._build_facts_url(f"users/{user_key}")
        response = await super().get_async(url)
        return UserRead.from_dict(response.json())

    def create(self, user: Union[UserCreate, Dict[str, Any]]) -> UserRead:
        """
        Create a new user.

        Args:
            user: User data.

        Returns:
            The created user.
        """
        if isinstance(user, UserCreate):
            user_data = user.to_dict()
        else:
            user_data = user

        url = self._build_facts_url("users")
        response = self.post(url, json=user_data)
        return UserRead.from_dict(response.json())

    async def create_async(self, user: Union[UserCreate, Dict[str, Any]]) -> UserRead:
        """
        Create a new user (async).

        Args:
            user: User data.

        Returns:
            The created user.
        """
        if isinstance(user, UserCreate):
            user_data = user.to_dict()
        else:
            user_data = user

        url = self._build_facts_url("users")
        response = await self.post_async(url, json=user_data)
        return UserRead.from_dict(response.json())

    def update(self, user_key: str, user: Union[UserUpdate, Dict[str, Any]]) -> UserRead:
        """
        Update an existing user.

        Args:
            user_key: The user key.
            user: User update data.

        Returns:
            The updated user.
        """
        if isinstance(user, UserUpdate):
            user_data = user.to_dict()
        else:
            user_data = user

        url = self._build_facts_url(f"users/{user_key}")
        response = self.patch(url, json=user_data)
        return UserRead.from_dict(response.json())

    async def update_async(self, user_key: str, user: Union[UserUpdate, Dict[str, Any]]) -> UserRead:
        """
        Update an existing user (async).

        Args:
            user_key: The user key.
            user: User update data.

        Returns:
            The updated user.
        """
        if isinstance(user, UserUpdate):
            user_data = user.to_dict()
        else:
            user_data = user

        url = self._build_facts_url(f"users/{user_key}")
        response = await self.patch_async(url, json=user_data)
        return UserRead.from_dict(response.json())

    def delete(self, user_key: str) -> None:
        """
        Delete a user.

        Args:
            user_key: The user key.
        """
        url = self._build_facts_url(f"users/{user_key}")
        super().delete(url)

    async def delete_async(self, user_key: str) -> None:
        """
        Delete a user (async).

        Args:
            user_key: The user key.
        """
        url = self._build_facts_url(f"users/{user_key}")
        await super().delete_async(url)

    def sync(self, user: Union[UserSync, Dict[str, Any]]) -> UserRead:
        """
        Sync a user (create or update with roles).

        Args:
            user: User sync data including roles.

        Returns:
            The synced user.
        """
        if isinstance(user, UserSync):
            user_data = user.to_dict()
        else:
            user_data = user

        url = self._build_facts_url("users")
        response = self.put(url, json=user_data)
        return UserRead.from_dict(response.json())

    async def sync_async(self, user: Union[UserSync, Dict[str, Any]]) -> UserRead:
        """
        Sync a user (create or update with roles) (async).

        Args:
            user: User sync data including roles.

        Returns:
            The synced user.
        """
        if isinstance(user, UserSync):
            user_data = user.to_dict()
        else:
            user_data = user

        url = self._build_facts_url("users")
        response = await self.put_async(url, json=user_data)
        return UserRead.from_dict(response.json())

    def assign_role(
        self,
        user_key: str,
        role: str,
        *,
        tenant: Optional[str] = None,
        resource_instance: Optional[str] = None,
    ) -> RoleAssignment:
        """
        Assign a role to a user.

        Args:
            user_key: The user key.
            role: The role key.
            tenant: The tenant key (optional).
            resource_instance: The resource instance key (optional).

        Returns:
            The role assignment.
        """
        assignment = RoleAssignmentCreate(
            user=user_key,
            role=role,
            tenant=tenant,
            resource_instance=resource_instance,
        )
        url = self._build_facts_url("role_assignments")
        response = self.post(url, json=assignment.to_dict())
        return RoleAssignment.from_dict(response.json())

    async def assign_role_async(
        self,
        user_key: str,
        role: str,
        *,
        tenant: Optional[str] = None,
        resource_instance: Optional[str] = None,
    ) -> RoleAssignment:
        """
        Assign a role to a user (async).

        Args:
            user_key: The user key.
            role: The role key.
            tenant: The tenant key (optional).
            resource_instance: The resource instance key (optional).

        Returns:
            The role assignment.
        """
        assignment = RoleAssignmentCreate(
            user=user_key,
            role=role,
            tenant=tenant,
            resource_instance=resource_instance,
        )
        url = self._build_facts_url("role_assignments")
        response = await self.post_async(url, json=assignment.to_dict())
        return RoleAssignment.from_dict(response.json())

    def unassign_role(
        self,
        user_key: str,
        role: str,
        *,
        tenant: Optional[str] = None,
        resource_instance: Optional[str] = None,
    ) -> None:
        """
        Unassign a role from a user.

        Args:
            user_key: The user key.
            role: The role key.
            tenant: The tenant key (optional).
            resource_instance: The resource instance key (optional).
        """
        params: Dict[str, Any] = {
            "user": user_key,
            "role": role,
        }
        if tenant:
            params["tenant"] = tenant
        if resource_instance:
            params["resource_instance"] = resource_instance

        url = self._build_facts_url("role_assignments")
        self.request("DELETE", url, params=params)

    async def unassign_role_async(
        self,
        user_key: str,
        role: str,
        *,
        tenant: Optional[str] = None,
        resource_instance: Optional[str] = None,
    ) -> None:
        """
        Unassign a role from a user (async).

        Args:
            user_key: The user key.
            role: The role key.
            tenant: The tenant key (optional).
            resource_instance: The resource instance key (optional).
        """
        params: Dict[str, Any] = {
            "user": user_key,
            "role": role,
        }
        if tenant:
            params["tenant"] = tenant
        if resource_instance:
            params["resource_instance"] = resource_instance

        url = self._build_facts_url("role_assignments")
        await self.request_async("DELETE", url, params=params)

    def get_roles(self, user_key: str, *, tenant: Optional[str] = None) -> List[RoleAssignment]:
        """
        Get roles assigned to a user.

        Args:
            user_key: The user key.
            tenant: Filter by tenant key (optional).

        Returns:
            List of role assignments.
        """
        params: Dict[str, Any] = {"user": user_key}
        if tenant:
            params["tenant"] = tenant

        url = self._build_facts_url("role_assignments")
        response = super().get(url, params=params)
        data = response.json()

        # Handle both paginated and non-paginated responses
        if isinstance(data, list):
            return [RoleAssignment.from_dict(item) for item in data]
        return [RoleAssignment.from_dict(item) for item in data.get("data", [])]

    async def get_roles_async(self, user_key: str, *, tenant: Optional[str] = None) -> List[RoleAssignment]:
        """
        Get roles assigned to a user (async).

        Args:
            user_key: The user key.
            tenant: Filter by tenant key (optional).

        Returns:
            List of role assignments.
        """
        params: Dict[str, Any] = {"user": user_key}
        if tenant:
            params["tenant"] = tenant

        url = self._build_facts_url("role_assignments")
        response = await super().get_async(url, params=params)
        data = response.json()

        if isinstance(data, list):
            return [RoleAssignment.from_dict(item) for item in data]
        return [RoleAssignment.from_dict(item) for item in data.get("data", [])]
