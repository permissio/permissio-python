"""
Role Assignments API client for the Permissio.io SDK.
"""

from typing import Any, Dict, List, Optional, Union

from permissio.api.base import BaseApiClient
from permissio.config import PermissioConfig
from permissio.models.common import PaginatedResponse
from permissio.models.role_assignment import (
    RoleAssignmentCreate,
    RoleAssignmentRead,
)


class RoleAssignmentsApi(BaseApiClient):
    """
    API client for role assignment operations.

    Provides methods for creating, reading, and deleting role assignments.
    """

    def __init__(self, config: PermissioConfig) -> None:
        """Initialize the Role Assignments API client."""
        super().__init__(config)

    def list(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        user: Optional[str] = None,
        role: Optional[str] = None,
        tenant: Optional[str] = None,
        resource_instance: Optional[str] = None,
    ) -> PaginatedResponse[RoleAssignmentRead]:
        """
        List role assignments.

        Args:
            page: Page number (1-indexed).
            per_page: Number of items per page.
            user: Filter by user key.
            role: Filter by role key.
            tenant: Filter by tenant key.
            resource_instance: Filter by resource instance key.

        Returns:
            Paginated list of role assignments.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "include_total_count": "true",
        }
        if user:
            params["user"] = user
        if role:
            params["role"] = role
        if tenant:
            params["tenant"] = tenant
        if resource_instance:
            params["resource_instance"] = resource_instance

        url = self._build_facts_url("role_assignments")
        response = self.request("GET", url, params=params)
        data = response.json()
        return PaginatedResponse.from_dict(data, RoleAssignmentRead.from_dict)

    async def list_async(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        user: Optional[str] = None,
        role: Optional[str] = None,
        tenant: Optional[str] = None,
        resource_instance: Optional[str] = None,
    ) -> PaginatedResponse[RoleAssignmentRead]:
        """
        List role assignments (async).

        Args:
            page: Page number (1-indexed).
            per_page: Number of items per page.
            user: Filter by user key.
            role: Filter by role key.
            tenant: Filter by tenant key.
            resource_instance: Filter by resource instance key.

        Returns:
            Paginated list of role assignments.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        if user:
            params["user"] = user
        if role:
            params["role"] = role
        if tenant:
            params["tenant"] = tenant
        if resource_instance:
            params["resource_instance"] = resource_instance

        url = self._build_facts_url("role_assignments")
        response = await self.request_async("GET", url, params=params)
        data = response.json()
        return PaginatedResponse.from_dict(data, RoleAssignmentRead.from_dict)

    def assign(
        self,
        user: str,
        role: str,
        *,
        tenant: Optional[str] = None,
        resource_instance: Optional[str] = None,
    ) -> RoleAssignmentRead:
        """
        Assign a role to a user.

        Args:
            user: The user key.
            role: The role key.
            tenant: The tenant key (optional).
            resource_instance: The resource instance key (optional).

        Returns:
            The created role assignment.
        """
        assignment = RoleAssignmentCreate(
            user=user,
            role=role,
            tenant=tenant,
            resource_instance=resource_instance,
        )
        url = self._build_facts_url("role_assignments")
        response = self.post(url, json=assignment.to_dict())
        return RoleAssignmentRead.from_dict(response.json())

    async def assign_async(
        self,
        user: str,
        role: str,
        *,
        tenant: Optional[str] = None,
        resource_instance: Optional[str] = None,
    ) -> RoleAssignmentRead:
        """
        Assign a role to a user (async).

        Args:
            user: The user key.
            role: The role key.
            tenant: The tenant key (optional).
            resource_instance: The resource instance key (optional).

        Returns:
            The created role assignment.
        """
        assignment = RoleAssignmentCreate(
            user=user,
            role=role,
            tenant=tenant,
            resource_instance=resource_instance,
        )
        url = self._build_facts_url("role_assignments")
        response = await self.post_async(url, json=assignment.to_dict())
        return RoleAssignmentRead.from_dict(response.json())

    def unassign(
        self,
        user: str,
        role: str,
        *,
        tenant: Optional[str] = None,
        resource_instance: Optional[str] = None,
    ) -> None:
        """
        Unassign a role from a user.

        Args:
            user: The user key.
            role: The role key.
            tenant: The tenant key (optional).
            resource_instance: The resource instance key (optional).
        """
        params: Dict[str, Any] = {
            "user": user,
            "role": role,
        }
        if tenant:
            params["tenant"] = tenant
        if resource_instance:
            params["resource_instance"] = resource_instance

        url = self._build_facts_url("role_assignments")
        self.request("DELETE", url, params=params)

    async def unassign_async(
        self,
        user: str,
        role: str,
        *,
        tenant: Optional[str] = None,
        resource_instance: Optional[str] = None,
    ) -> None:
        """
        Unassign a role from a user (async).

        Args:
            user: The user key.
            role: The role key.
            tenant: The tenant key (optional).
            resource_instance: The resource instance key (optional).
        """
        params: Dict[str, Any] = {
            "user": user,
            "role": role,
        }
        if tenant:
            params["tenant"] = tenant
        if resource_instance:
            params["resource_instance"] = resource_instance

        url = self._build_facts_url("role_assignments")
        await self.request_async("DELETE", url, params=params)

    def bulk_assign(self, assignments: List[Union[RoleAssignmentCreate, Dict[str, Any]]]) -> List[RoleAssignmentRead]:
        """
        Bulk assign roles to users.

        Args:
            assignments: List of role assignments to create.

        Returns:
            List of created role assignments.
        """
        assignment_dicts = []
        for a in assignments:
            if isinstance(a, RoleAssignmentCreate):
                assignment_dicts.append(a.to_dict())
            else:
                assignment_dicts.append(a)

        url = self._build_facts_url("role_assignments/bulk")
        response = self.post(url, json={"assignments": assignment_dicts})
        data = response.json()

        if isinstance(data, list):
            return [RoleAssignmentRead.from_dict(item) for item in data]
        return [RoleAssignmentRead.from_dict(item) for item in data.get("data", [])]

    async def bulk_assign_async(self, assignments: List[Union[RoleAssignmentCreate, Dict[str, Any]]]) -> List[RoleAssignmentRead]:
        """
        Bulk assign roles to users (async).

        Args:
            assignments: List of role assignments to create.

        Returns:
            List of created role assignments.
        """
        assignment_dicts = []
        for a in assignments:
            if isinstance(a, RoleAssignmentCreate):
                assignment_dicts.append(a.to_dict())
            else:
                assignment_dicts.append(a)

        url = self._build_facts_url("role_assignments/bulk")
        response = await self.post_async(url, json={"assignments": assignment_dicts})
        data = response.json()

        if isinstance(data, list):
            return [RoleAssignmentRead.from_dict(item) for item in data]
        return [RoleAssignmentRead.from_dict(item) for item in data.get("data", [])]

    def bulk_unassign(self, assignments: List[Union[RoleAssignmentCreate, Dict[str, Any]]]) -> None:
        """
        Bulk unassign roles from users.

        Args:
            assignments: List of role assignments to remove.
        """
        assignment_dicts = []
        for a in assignments:
            if isinstance(a, RoleAssignmentCreate):
                assignment_dicts.append(a.to_dict())
            else:
                assignment_dicts.append(a)

        url = self._build_facts_url("role_assignments/bulk")
        self.request("DELETE", url, json={"assignments": assignment_dicts})

    async def bulk_unassign_async(self, assignments: List[Union[RoleAssignmentCreate, Dict[str, Any]]]) -> None:
        """
        Bulk unassign roles from users (async).

        Args:
            assignments: List of role assignments to remove.
        """
        assignment_dicts = []
        for a in assignments:
            if isinstance(a, RoleAssignmentCreate):
                assignment_dicts.append(a.to_dict())
            else:
                assignment_dicts.append(a)

        url = self._build_facts_url("role_assignments/bulk")
        await self.request_async("DELETE", url, json={"assignments": assignment_dicts})

    def list_detailed(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        user: Optional[str] = None,
        role: Optional[str] = None,
        tenant: Optional[str] = None,
    ) -> PaginatedResponse[RoleAssignmentRead]:
        """
        List role assignments with detailed information.

        Args:
            page: Page number (1-indexed).
            per_page: Number of items per page.
            user: Filter by user key.
            role: Filter by role key.
            tenant: Filter by tenant key.

        Returns:
            Paginated list of detailed role assignments.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        if user:
            params["user"] = user
        if role:
            params["role"] = role
        if tenant:
            params["tenant"] = tenant

        url = self._build_facts_url("role_assignments/detailed")
        response = self.get(url, params=params)
        data = response.json()
        return PaginatedResponse.from_dict(data, RoleAssignmentRead.from_dict)

    async def list_detailed_async(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        user: Optional[str] = None,
        role: Optional[str] = None,
        tenant: Optional[str] = None,
    ) -> PaginatedResponse[RoleAssignmentRead]:
        """
        List role assignments with detailed information (async).

        Args:
            page: Page number (1-indexed).
            per_page: Number of items per page.
            user: Filter by user key.
            role: Filter by role key.
            tenant: Filter by tenant key.

        Returns:
            Paginated list of detailed role assignments.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        if user:
            params["user"] = user
        if role:
            params["role"] = role
        if tenant:
            params["tenant"] = tenant

        url = self._build_facts_url("role_assignments/detailed")
        response = await self.get_async(url, params=params)
        data = response.json()
        return PaginatedResponse.from_dict(data, RoleAssignmentRead.from_dict)
