"""
Main Permis.io SDK client.
"""

from typing import Optional, Dict, Any, Union

from permisio.config import PermisConfig, ConfigBuilder, resolve_config
from permisio.api.base import BaseApiClient
from permisio.api.users import UsersApi
from permisio.api.tenants import TenantsApi
from permisio.api.roles import RolesApi
from permisio.api.resources import ResourcesApi
from permisio.api.role_assignments import RoleAssignmentsApi
from permisio.models.check import CheckRequest, CheckResponse, BulkCheckRequest, BulkCheckResponse
from permisio.enforcement.models import (
    CheckUser,
    CheckResource,
    UserBuilder,
    ResourceBuilder,
    normalize_user,
    normalize_resource,
    normalize_context,
)


class PermisApi:
    """
    Container for all API clients.

    Provides access to all resource-specific API clients.
    """

    def __init__(self, config: PermisConfig) -> None:
        """
        Initialize all API clients.

        Args:
            config: SDK configuration.
        """
        self._config = config
        self._users = UsersApi(config)
        self._tenants = TenantsApi(config)
        self._roles = RolesApi(config)
        self._resources = ResourcesApi(config)
        self._role_assignments = RoleAssignmentsApi(config)

    @property
    def users(self) -> UsersApi:
        """Get the Users API client."""
        return self._users

    @property
    def tenants(self) -> TenantsApi:
        """Get the Tenants API client."""
        return self._tenants

    @property
    def roles(self) -> RolesApi:
        """Get the Roles API client."""
        return self._roles

    @property
    def resources(self) -> ResourcesApi:
        """Get the Resources API client."""
        return self._resources

    @property
    def role_assignments(self) -> RoleAssignmentsApi:
        """Get the Role Assignments API client."""
        return self._role_assignments

    def close(self) -> None:
        """Close all API clients."""
        self._users.close()
        self._tenants.close()
        self._roles.close()
        self._resources.close()
        self._role_assignments.close()

    async def close_async(self) -> None:
        """Close all API clients (async)."""
        await self._users.close_async()
        await self._tenants.close_async()
        await self._roles.close_async()
        await self._resources.close_async()
        await self._role_assignments.close_async()


class Permis:
    """
    Main Permis.io SDK client.

    This is the primary entry point for interacting with the Permis.io API.
    It provides both permission checking methods and access to resource APIs.

    Example:
        # Create client
        permis = Permis(
            token="permis_key_your_api_key",
            project_id="my-project",
            environment_id="production",
        )

        # Check permission
        if permis.check("user@example.com", "read", "document"):
            print("Access granted")

        # Use API clients
        users = permis.api.users.list()

        # Close when done
        permis.close()

    Example with context manager:
        with Permis(token="permis_key_your_api_key") as permis:
            allowed = permis.check("user@example.com", "read", "document")
    """

    def __init__(
        self,
        token: Optional[str] = None,
        *,
        config: Optional[Union[PermisConfig, Dict[str, Any]]] = None,
        api_url: Optional[str] = None,
        project_id: Optional[str] = None,
        environment_id: Optional[str] = None,
        timeout: Optional[float] = None,
        debug: bool = False,
        retry_attempts: Optional[int] = None,
        throw_on_error: bool = True,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize the Permis.io SDK client.

        Args:
            token: API key for authentication. Required if config is not provided.
            config: Optional pre-built PermisConfig or config dictionary.
            api_url: Base URL for the API.
            project_id: Project identifier.
            environment_id: Environment identifier.
            timeout: Request timeout in seconds.
            debug: Enable debug logging.
            retry_attempts: Number of retry attempts.
            throw_on_error: Whether to raise exceptions on API errors.
            custom_headers: Additional headers to include in requests.
        """
        # Build configuration
        if config is not None:
            self._config = resolve_config(config)
        elif token is not None:
            builder = ConfigBuilder(token)
            if api_url:
                builder.with_api_url(api_url)
            if project_id:
                builder.with_project_id(project_id)
            if environment_id:
                builder.with_environment_id(environment_id)
            if timeout:
                builder.with_timeout(timeout)
            builder.with_debug(debug)
            if retry_attempts is not None:
                builder.with_retry_attempts(retry_attempts)
            builder.with_throw_on_error(throw_on_error)
            if custom_headers:
                builder.with_custom_headers(custom_headers)
            self._config = builder.build()
        else:
            raise ValueError("Either 'token' or 'config' must be provided")

        # Initialize API container
        self._api = PermisApi(self._config)

        # Create base client for check operations
        self._base_client = BaseApiClient(self._config)

    @property
    def config(self) -> PermisConfig:
        """Get the SDK configuration."""
        return self._config

    @property
    def api(self) -> PermisApi:
        """Get the API clients container."""
        return self._api

    def check(
        self,
        user: Union[str, Dict[str, Any], CheckUser, UserBuilder],
        action: str,
        resource: Union[str, Dict[str, Any], CheckResource, ResourceBuilder],
        *,
        tenant: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Check if a user has permission to perform an action on a resource.

        Args:
            user: User identifier (key, dict with attributes, or CheckUser).
            action: Action to check permission for.
            resource: Resource to check (type, dict with attributes, or CheckResource).
            tenant: Tenant key (optional, can also be specified in resource).
            context: Additional context for the check.

        Returns:
            True if the action is allowed, False otherwise.

        Example:
            # Simple check
            allowed = permis.check("user@example.com", "read", "document")

            # With tenant
            allowed = permis.check("user@example.com", "read", "document", tenant="acme")

            # With resource instance
            allowed = permis.check(
                "user@example.com",
                "read",
                {"type": "document", "key": "doc-123"}
            )

            # With ABAC
            allowed = permis.check(
                {"key": "user@example.com", "attributes": {"department": "engineering"}},
                "read",
                {"type": "document", "attributes": {"classification": "internal"}}
            )
        """
        response = self.check_with_details(user, action, resource, tenant=tenant, context=context)
        return response.allowed

    async def check_async(
        self,
        user: Union[str, Dict[str, Any], CheckUser, UserBuilder],
        action: str,
        resource: Union[str, Dict[str, Any], CheckResource, ResourceBuilder],
        *,
        tenant: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Check if a user has permission to perform an action on a resource (async).

        Args:
            user: User identifier (key, dict with attributes, or CheckUser).
            action: Action to check permission for.
            resource: Resource to check (type, dict with attributes, or CheckResource).
            tenant: Tenant key (optional, can also be specified in resource).
            context: Additional context for the check.

        Returns:
            True if the action is allowed, False otherwise.
        """
        response = await self.check_with_details_async(user, action, resource, tenant=tenant, context=context)
        return response.allowed

    def check_with_details(
        self,
        user: Union[str, Dict[str, Any], CheckUser, UserBuilder],
        action: str,
        resource: Union[str, Dict[str, Any], CheckResource, ResourceBuilder],
        *,
        tenant: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> CheckResponse:
        """
        Check permission and get detailed response.

        Args:
            user: User identifier (key, dict with attributes, or CheckUser).
            action: Action to check permission for.
            resource: Resource to check (type, dict with attributes, or CheckResource).
            tenant: Tenant key (optional, can also be specified in resource).
            context: Additional context for the check.

        Returns:
            CheckResponse with allowed status and additional details.
        """
        # Normalize inputs
        user_data = normalize_user(user)
        resource_data = normalize_resource(resource)
        context_data = normalize_context(context)

        # Add tenant to resource if provided
        if tenant and "tenant" not in resource_data:
            resource_data["tenant"] = tenant

        # Build request
        request_data = {
            "user": user_data,
            "action": action,
            "resource": resource_data,
        }
        if context_data:
            request_data["context"] = context_data

        # Make request
        url = self._base_client._build_allowed_url()
        response = self._base_client.post(url, json=request_data)
        return CheckResponse.from_dict(response.json())

    async def check_with_details_async(
        self,
        user: Union[str, Dict[str, Any], CheckUser, UserBuilder],
        action: str,
        resource: Union[str, Dict[str, Any], CheckResource, ResourceBuilder],
        *,
        tenant: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> CheckResponse:
        """
        Check permission and get detailed response (async).

        Args:
            user: User identifier (key, dict with attributes, or CheckUser).
            action: Action to check permission for.
            resource: Resource to check (type, dict with attributes, or CheckResource).
            tenant: Tenant key (optional, can also be specified in resource).
            context: Additional context for the check.

        Returns:
            CheckResponse with allowed status and additional details.
        """
        # Normalize inputs
        user_data = normalize_user(user)
        resource_data = normalize_resource(resource)
        context_data = normalize_context(context)

        # Add tenant to resource if provided
        if tenant and "tenant" not in resource_data:
            resource_data["tenant"] = tenant

        # Build request
        request_data = {
            "user": user_data,
            "action": action,
            "resource": resource_data,
        }
        if context_data:
            request_data["context"] = context_data

        # Make request
        url = self._base_client._build_allowed_url()
        response = await self._base_client.post_async(url, json=request_data)
        return CheckResponse.from_dict(response.json())

    def bulk_check(
        self,
        checks: list,
    ) -> BulkCheckResponse:
        """
        Check multiple permissions in a single request.

        Args:
            checks: List of check requests (dicts or CheckRequest objects).

        Returns:
            BulkCheckResponse with results for each check.

        Example:
            results = permis.bulk_check([
                {"user": "user1", "action": "read", "resource": "document"},
                {"user": "user1", "action": "write", "resource": "document"},
                {"user": "user2", "action": "read", "resource": "document"},
            ])
            for result in results.results:
                print(f"Allowed: {result.allowed}")
        """
        check_dicts = []
        for check in checks:
            if hasattr(check, "to_dict"):
                check_dicts.append(check.to_dict())
            elif isinstance(check, dict):
                # Normalize the check
                normalized = {
                    "user": normalize_user(check.get("user", "")),
                    "action": check.get("action", ""),
                    "resource": normalize_resource(check.get("resource", "")),
                }
                if "tenant" in check:
                    normalized["tenant"] = check["tenant"]
                if "context" in check:
                    normalized["context"] = check["context"]
                check_dicts.append(normalized)
            else:
                raise ValueError(f"Invalid check type: {type(check)}")

        url = self._base_client._build_allowed_url() + "/bulk"
        response = self._base_client.post(url, json={"checks": check_dicts})
        return BulkCheckResponse.from_dict(response.json())

    async def bulk_check_async(
        self,
        checks: list,
    ) -> BulkCheckResponse:
        """
        Check multiple permissions in a single request (async).

        Args:
            checks: List of check requests (dicts or CheckRequest objects).

        Returns:
            BulkCheckResponse with results for each check.
        """
        check_dicts = []
        for check in checks:
            if hasattr(check, "to_dict"):
                check_dicts.append(check.to_dict())
            elif isinstance(check, dict):
                normalized = {
                    "user": normalize_user(check.get("user", "")),
                    "action": check.get("action", ""),
                    "resource": normalize_resource(check.get("resource", "")),
                }
                if "tenant" in check:
                    normalized["tenant"] = check["tenant"]
                if "context" in check:
                    normalized["context"] = check["context"]
                check_dicts.append(normalized)
            else:
                raise ValueError(f"Invalid check type: {type(check)}")

        url = self._base_client._build_allowed_url() + "/bulk"
        response = await self._base_client.post_async(url, json={"checks": check_dicts})
        return BulkCheckResponse.from_dict(response.json())

    def close(self) -> None:
        """Close the client and release resources."""
        self._base_client.close()
        self._api.close()

    async def close_async(self) -> None:
        """Close the client and release resources (async)."""
        await self._base_client.close_async()
        await self._api.close_async()

    def __enter__(self) -> "Permis":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    async def __aenter__(self) -> "Permis":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close_async()

    # Convenience methods that mirror Permit.io SDK

    def sync_user(self, user: Union[Dict[str, Any], Any]) -> Any:
        """
        Sync a user (create or update).

        This is a convenience method that wraps api.users.sync().

        Args:
            user: User data to sync.

        Returns:
            The synced user.
        """
        return self._api.users.sync(user)

    async def sync_user_async(self, user: Union[Dict[str, Any], Any]) -> Any:
        """
        Sync a user (create or update) (async).

        Args:
            user: User data to sync.

        Returns:
            The synced user.
        """
        return await self._api.users.sync_async(user)

    def assign_role(
        self,
        user: str,
        role: str,
        *,
        tenant: Optional[str] = None,
        resource_instance: Optional[str] = None,
    ) -> Any:
        """
        Assign a role to a user.

        This is a convenience method that wraps api.role_assignments.assign().

        Args:
            user: User key.
            role: Role key.
            tenant: Tenant key (optional).
            resource_instance: Resource instance key (optional).

        Returns:
            The role assignment.
        """
        return self._api.role_assignments.assign(
            user, role, tenant=tenant, resource_instance=resource_instance
        )

    async def assign_role_async(
        self,
        user: str,
        role: str,
        *,
        tenant: Optional[str] = None,
        resource_instance: Optional[str] = None,
    ) -> Any:
        """
        Assign a role to a user (async).

        Args:
            user: User key.
            role: Role key.
            tenant: Tenant key (optional).
            resource_instance: Resource instance key (optional).

        Returns:
            The role assignment.
        """
        return await self._api.role_assignments.assign_async(
            user, role, tenant=tenant, resource_instance=resource_instance
        )

    def unassign_role(
        self,
        user: str,
        role: str,
        *,
        tenant: Optional[str] = None,
        resource_instance: Optional[str] = None,
    ) -> None:
        """
        Unassign a role from a user.

        This is a convenience method that wraps api.role_assignments.unassign().

        Args:
            user: User key.
            role: Role key.
            tenant: Tenant key (optional).
            resource_instance: Resource instance key (optional).
        """
        self._api.role_assignments.unassign(
            user, role, tenant=tenant, resource_instance=resource_instance
        )

    async def unassign_role_async(
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
            user: User key.
            role: Role key.
            tenant: Tenant key (optional).
            resource_instance: Resource instance key (optional).
        """
        await self._api.role_assignments.unassign_async(
            user, role, tenant=tenant, resource_instance=resource_instance
        )

    def create_tenant(self, tenant: Union[Dict[str, Any], Any]) -> Any:
        """
        Create a tenant.

        This is a convenience method that wraps api.tenants.create().

        Args:
            tenant: Tenant data.

        Returns:
            The created tenant.
        """
        return self._api.tenants.create(tenant)

    async def create_tenant_async(self, tenant: Union[Dict[str, Any], Any]) -> Any:
        """
        Create a tenant (async).

        Args:
            tenant: Tenant data.

        Returns:
            The created tenant.
        """
        return await self._api.tenants.create_async(tenant)
