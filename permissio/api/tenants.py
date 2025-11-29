"""
Tenants API client for the Permissio.io SDK.
"""

from typing import Optional, Dict, Any, Union

from permissio.api.base import BaseApiClient
from permissio.config import PermissioConfig
from permissio.models.tenant import Tenant, TenantCreate, TenantUpdate, TenantRead
from permissio.models.common import PaginatedResponse


class TenantsApi(BaseApiClient):
    """
    API client for tenant operations.

    Provides methods for creating, reading, updating, and deleting tenants.
    """

    def __init__(self, config: PermissioConfig) -> None:
        """Initialize the Tenants API client."""
        super().__init__(config)

    def list(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
    ) -> PaginatedResponse[TenantRead]:
        """
        List tenants.

        Args:
            page: Page number (1-indexed).
            per_page: Number of items per page.
            search: Search query string.

        Returns:
            Paginated list of tenants.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "include_total_count": "true",
        }
        if search:
            params["search"] = search

        url = self._build_facts_url("tenants")
        response = self.request("GET", url, params=params)
        data = response.json()
        return PaginatedResponse.from_dict(data, TenantRead.from_dict)

    async def list_async(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
    ) -> PaginatedResponse[TenantRead]:
        """
        List tenants (async).

        Args:
            page: Page number (1-indexed).
            per_page: Number of items per page.
            search: Search query string.

        Returns:
            Paginated list of tenants.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "include_total_count": "true",
        }
        if search:
            params["search"] = search

        url = self._build_facts_url("tenants")
        response = await self.request_async("GET", url, params=params)
        data = response.json()
        return PaginatedResponse.from_dict(data, TenantRead.from_dict)

    def get(self, tenant_key: str) -> TenantRead:
        """
        Get a tenant by key.

        Args:
            tenant_key: The tenant key.

        Returns:
            The tenant.
        """
        url = self._build_facts_url(f"tenants/{tenant_key}")
        response = super().get(url)
        return TenantRead.from_dict(response.json())

    async def get_async(self, tenant_key: str) -> TenantRead:
        """
        Get a tenant by key (async).

        Args:
            tenant_key: The tenant key.

        Returns:
            The tenant.
        """
        url = self._build_facts_url(f"tenants/{tenant_key}")
        response = await super().get_async(url)
        return TenantRead.from_dict(response.json())

    def create(self, tenant: Union[TenantCreate, Dict[str, Any]]) -> TenantRead:
        """
        Create a new tenant.

        Args:
            tenant: Tenant data.

        Returns:
            The created tenant.
        """
        if isinstance(tenant, TenantCreate):
            tenant_data = tenant.to_dict()
        else:
            tenant_data = tenant

        url = self._build_facts_url("tenants")
        response = self.post(url, json=tenant_data)
        return TenantRead.from_dict(response.json())

    async def create_async(self, tenant: Union[TenantCreate, Dict[str, Any]]) -> TenantRead:
        """
        Create a new tenant (async).

        Args:
            tenant: Tenant data.

        Returns:
            The created tenant.
        """
        if isinstance(tenant, TenantCreate):
            tenant_data = tenant.to_dict()
        else:
            tenant_data = tenant

        url = self._build_facts_url("tenants")
        response = await self.post_async(url, json=tenant_data)
        return TenantRead.from_dict(response.json())

    def update(self, tenant_key: str, tenant: Union[TenantUpdate, Dict[str, Any]]) -> TenantRead:
        """
        Update an existing tenant.

        Args:
            tenant_key: The tenant key.
            tenant: Tenant update data.

        Returns:
            The updated tenant.
        """
        if isinstance(tenant, TenantUpdate):
            tenant_data = tenant.to_dict()
        else:
            tenant_data = tenant

        url = self._build_facts_url(f"tenants/{tenant_key}")
        response = self.patch(url, json=tenant_data)
        return TenantRead.from_dict(response.json())

    async def update_async(self, tenant_key: str, tenant: Union[TenantUpdate, Dict[str, Any]]) -> TenantRead:
        """
        Update an existing tenant (async).

        Args:
            tenant_key: The tenant key.
            tenant: Tenant update data.

        Returns:
            The updated tenant.
        """
        if isinstance(tenant, TenantUpdate):
            tenant_data = tenant.to_dict()
        else:
            tenant_data = tenant

        url = self._build_facts_url(f"tenants/{tenant_key}")
        response = await self.patch_async(url, json=tenant_data)
        return TenantRead.from_dict(response.json())

    def delete(self, tenant_key: str) -> None:
        """
        Delete a tenant.

        Args:
            tenant_key: The tenant key.
        """
        url = self._build_facts_url(f"tenants/{tenant_key}")
        super().delete(url)

    async def delete_async(self, tenant_key: str) -> None:
        """
        Delete a tenant (async).

        Args:
            tenant_key: The tenant key.
        """
        url = self._build_facts_url(f"tenants/{tenant_key}")
        await super().delete_async(url)
