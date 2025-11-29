"""
Resources API client for the Permis.io SDK.
"""

from typing import Optional, Dict, Any, Union, List

from permisio.api.base import BaseApiClient
from permisio.config import PermisConfig
from permisio.models.resource import (
    Resource,
    ResourceCreate,
    ResourceUpdate,
    ResourceRead,
    ResourceAction,
    ResourceAttribute,
)
from permisio.models.common import PaginatedResponse


class ResourcesApi(BaseApiClient):
    """
    API client for resource type operations.

    Provides methods for creating, reading, updating, and deleting resource types,
    as well as managing resource actions and attributes.
    Resources are part of the Schema API.
    """

    def __init__(self, config: PermisConfig) -> None:
        """Initialize the Resources API client."""
        super().__init__(config)

    def list(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
    ) -> PaginatedResponse[ResourceRead]:
        """
        List resource types.

        Args:
            page: Page number (1-indexed).
            per_page: Number of items per page.
            search: Search query string.

        Returns:
            Paginated list of resources.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        if search:
            params["search"] = search

        url = self._build_schema_url("resources")
        response = self.get(url, params=params)
        data = response.json()
        return PaginatedResponse.from_dict(data, ResourceRead.from_dict)

    async def list_async(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
    ) -> PaginatedResponse[ResourceRead]:
        """
        List resource types (async).

        Args:
            page: Page number (1-indexed).
            per_page: Number of items per page.
            search: Search query string.

        Returns:
            Paginated list of resources.
        """
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        if search:
            params["search"] = search

        url = self._build_schema_url("resources")
        response = await self.get_async(url, params=params)
        data = response.json()
        return PaginatedResponse.from_dict(data, ResourceRead.from_dict)

    def get(self, resource_key: str) -> ResourceRead:
        """
        Get a resource type by key.

        Args:
            resource_key: The resource key.

        Returns:
            The resource.
        """
        url = self._build_schema_url(f"resources/{resource_key}")
        response = super().get(url)
        return ResourceRead.from_dict(response.json())

    async def get_async(self, resource_key: str) -> ResourceRead:
        """
        Get a resource type by key (async).

        Args:
            resource_key: The resource key.

        Returns:
            The resource.
        """
        url = self._build_schema_url(f"resources/{resource_key}")
        response = await super().get_async(url)
        return ResourceRead.from_dict(response.json())

    def create(self, resource: Union[ResourceCreate, Dict[str, Any]]) -> ResourceRead:
        """
        Create a new resource type.

        Args:
            resource: Resource data.

        Returns:
            The created resource.
        """
        if isinstance(resource, ResourceCreate):
            resource_data = resource.to_dict()
        else:
            resource_data = resource

        url = self._build_schema_url("resources")
        response = self.post(url, json=resource_data)
        return ResourceRead.from_dict(response.json())

    async def create_async(self, resource: Union[ResourceCreate, Dict[str, Any]]) -> ResourceRead:
        """
        Create a new resource type (async).

        Args:
            resource: Resource data.

        Returns:
            The created resource.
        """
        if isinstance(resource, ResourceCreate):
            resource_data = resource.to_dict()
        else:
            resource_data = resource

        url = self._build_schema_url("resources")
        response = await self.post_async(url, json=resource_data)
        return ResourceRead.from_dict(response.json())

    def update(self, resource_key: str, resource: Union[ResourceUpdate, Dict[str, Any]]) -> ResourceRead:
        """
        Update an existing resource type.

        Args:
            resource_key: The resource key.
            resource: Resource update data.

        Returns:
            The updated resource.
        """
        if isinstance(resource, ResourceUpdate):
            resource_data = resource.to_dict()
        else:
            resource_data = resource

        url = self._build_schema_url(f"resources/{resource_key}")
        response = self.patch(url, json=resource_data)
        return ResourceRead.from_dict(response.json())

    async def update_async(self, resource_key: str, resource: Union[ResourceUpdate, Dict[str, Any]]) -> ResourceRead:
        """
        Update an existing resource type (async).

        Args:
            resource_key: The resource key.
            resource: Resource update data.

        Returns:
            The updated resource.
        """
        if isinstance(resource, ResourceUpdate):
            resource_data = resource.to_dict()
        else:
            resource_data = resource

        url = self._build_schema_url(f"resources/{resource_key}")
        response = await self.patch_async(url, json=resource_data)
        return ResourceRead.from_dict(response.json())

    def delete(self, resource_key: str) -> None:
        """
        Delete a resource type.

        Args:
            resource_key: The resource key.
        """
        url = self._build_schema_url(f"resources/{resource_key}")
        super().delete(url)

    async def delete_async(self, resource_key: str) -> None:
        """
        Delete a resource type (async).

        Args:
            resource_key: The resource key.
        """
        url = self._build_schema_url(f"resources/{resource_key}")
        await super().delete_async(url)

    # Action management

    def list_actions(self, resource_key: str) -> List[ResourceAction]:
        """
        List actions for a resource type.

        Args:
            resource_key: The resource key.

        Returns:
            List of actions.
        """
        url = self._build_schema_url(f"resources/{resource_key}/actions")
        response = super().get(url)
        data = response.json()
        if isinstance(data, list):
            return [ResourceAction.from_dict(a) for a in data]
        return [ResourceAction.from_dict(a) for a in data.get("data", [])]

    async def list_actions_async(self, resource_key: str) -> List[ResourceAction]:
        """
        List actions for a resource type (async).

        Args:
            resource_key: The resource key.

        Returns:
            List of actions.
        """
        url = self._build_schema_url(f"resources/{resource_key}/actions")
        response = await super().get_async(url)
        data = response.json()
        if isinstance(data, list):
            return [ResourceAction.from_dict(a) for a in data]
        return [ResourceAction.from_dict(a) for a in data.get("data", [])]

    def create_action(self, resource_key: str, action: Union[ResourceAction, Dict[str, Any]]) -> ResourceAction:
        """
        Create an action for a resource type.

        Args:
            resource_key: The resource key.
            action: Action data.

        Returns:
            The created action.
        """
        if isinstance(action, ResourceAction):
            action_data = action.to_dict()
        else:
            action_data = action

        url = self._build_schema_url(f"resources/{resource_key}/actions")
        response = self.post(url, json=action_data)
        return ResourceAction.from_dict(response.json())

    async def create_action_async(self, resource_key: str, action: Union[ResourceAction, Dict[str, Any]]) -> ResourceAction:
        """
        Create an action for a resource type (async).

        Args:
            resource_key: The resource key.
            action: Action data.

        Returns:
            The created action.
        """
        if isinstance(action, ResourceAction):
            action_data = action.to_dict()
        else:
            action_data = action

        url = self._build_schema_url(f"resources/{resource_key}/actions")
        response = await self.post_async(url, json=action_data)
        return ResourceAction.from_dict(response.json())

    def delete_action(self, resource_key: str, action_key: str) -> None:
        """
        Delete an action from a resource type.

        Args:
            resource_key: The resource key.
            action_key: The action key.
        """
        url = self._build_schema_url(f"resources/{resource_key}/actions/{action_key}")
        super().delete(url)

    async def delete_action_async(self, resource_key: str, action_key: str) -> None:
        """
        Delete an action from a resource type (async).

        Args:
            resource_key: The resource key.
            action_key: The action key.
        """
        url = self._build_schema_url(f"resources/{resource_key}/actions/{action_key}")
        await super().delete_async(url)

    # Attribute management

    def list_attributes(self, resource_key: str) -> List[ResourceAttribute]:
        """
        List attributes for a resource type.

        Args:
            resource_key: The resource key.

        Returns:
            List of attributes.
        """
        url = self._build_schema_url(f"resources/{resource_key}/attributes")
        response = super().get(url)
        data = response.json()
        if isinstance(data, list):
            return [ResourceAttribute.from_dict(a) for a in data]
        return [ResourceAttribute.from_dict(a) for a in data.get("data", [])]

    async def list_attributes_async(self, resource_key: str) -> List[ResourceAttribute]:
        """
        List attributes for a resource type (async).

        Args:
            resource_key: The resource key.

        Returns:
            List of attributes.
        """
        url = self._build_schema_url(f"resources/{resource_key}/attributes")
        response = await super().get_async(url)
        data = response.json()
        if isinstance(data, list):
            return [ResourceAttribute.from_dict(a) for a in data]
        return [ResourceAttribute.from_dict(a) for a in data.get("data", [])]

    def create_attribute(self, resource_key: str, attribute: Union[ResourceAttribute, Dict[str, Any]]) -> ResourceAttribute:
        """
        Create an attribute for a resource type.

        Args:
            resource_key: The resource key.
            attribute: Attribute data.

        Returns:
            The created attribute.
        """
        if isinstance(attribute, ResourceAttribute):
            attribute_data = attribute.to_dict()
        else:
            attribute_data = attribute

        url = self._build_schema_url(f"resources/{resource_key}/attributes")
        response = self.post(url, json=attribute_data)
        return ResourceAttribute.from_dict(response.json())

    async def create_attribute_async(self, resource_key: str, attribute: Union[ResourceAttribute, Dict[str, Any]]) -> ResourceAttribute:
        """
        Create an attribute for a resource type (async).

        Args:
            resource_key: The resource key.
            attribute: Attribute data.

        Returns:
            The created attribute.
        """
        if isinstance(attribute, ResourceAttribute):
            attribute_data = attribute.to_dict()
        else:
            attribute_data = attribute

        url = self._build_schema_url(f"resources/{resource_key}/attributes")
        response = await self.post_async(url, json=attribute_data)
        return ResourceAttribute.from_dict(response.json())

    def delete_attribute(self, resource_key: str, attribute_key: str) -> None:
        """
        Delete an attribute from a resource type.

        Args:
            resource_key: The resource key.
            attribute_key: The attribute key.
        """
        url = self._build_schema_url(f"resources/{resource_key}/attributes/{attribute_key}")
        super().delete(url)

    async def delete_attribute_async(self, resource_key: str, attribute_key: str) -> None:
        """
        Delete an attribute from a resource type (async).

        Args:
            resource_key: The resource key.
            attribute_key: The attribute key.
        """
        url = self._build_schema_url(f"resources/{resource_key}/attributes/{attribute_key}")
        await super().delete_async(url)
