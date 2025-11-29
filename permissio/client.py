"""
Main Permissio.io SDK client.
"""

from typing import Optional, Dict, Any, Union

from permissio.config import PermissioConfig, ConfigBuilder, resolve_config
from permissio.api.base import BaseApiClient
from permissio.api.users import UsersApi
from permissio.api.tenants import TenantsApi
from permissio.api.roles import RolesApi
from permissio.api.resources import ResourcesApi
from permissio.api.role_assignments import RoleAssignmentsApi
from permissio.models.check import CheckRequest, CheckResponse, BulkCheckRequest, BulkCheckResponse
from permissio.enforcement.models import (
    CheckUser,
    CheckResource,
    UserBuilder,
    ResourceBuilder,
    normalize_user,
    normalize_resource,
    normalize_context,
)


class PermissioApi:
    """
    Container for all API clients.

    Provides access to all resource-specific API clients.
    """

    def __init__(self, config: PermissioConfig) -> None:
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


class Permissio:
    """
    Main Permissio.io SDK client.

    This is the primary entry point for interacting with the Permissio.io API.
    It provides both permission checking methods and access to resource APIs.

    Example:
        # Create client
        permissio = Permissio(
            token="permis_key_your_api_key",
            project_id="my-project",
            environment_id="production",
        )

        # Check permission
        if permissio.check("user@example.com", "read", "document"):
            print("Access granted")

        # Use API clients
        users = permissio.api.users.list()

        # Close when done
        permissio.close()

    Example with context manager:
        with Permissio(token="permis_key_your_api_key") as permissio:
            allowed = permissio.check("user@example.com", "read", "document")
    """

    def __init__(
        self,
        token: Optional[str] = None,
        *,
        config: Optional[Union[PermissioConfig, Dict[str, Any]]] = None,
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
        Initialize the Permissio.io SDK client.

        Args:
            token: API key for authentication. Required if config is not provided.
            config: Optional pre-built PermissioConfig or config dictionary.
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
        self._api = PermissioApi(self._config)

        # Create base client for check operations
        self._base_client = BaseApiClient(self._config)

        # Track if scope has been initialized
        self._scope_initialized = False

    def init(self) -> None:
        """
        Initialize the SDK by fetching project/environment scope from the API key.

        This method fetches the project_id and environment_id from the API key
        if they are not already set. Call this before using the SDK if you haven't
        provided project_id and environment_id in the configuration.

        Example:
            permissio = Permissio(token="permis_key_your_api_key")
            permissio.init()  # Fetches project/environment from API key
            # Now you can use the SDK
        """
        if self._scope_initialized:
            return

        if self._config.has_scope():
            self._scope_initialized = True
            return

        self._fetch_and_set_scope()
        self._scope_initialized = True

    async def init_async(self) -> None:
        """
        Initialize the SDK by fetching project/environment scope from the API key (async).

        This method fetches the project_id and environment_id from the API key
        if they are not already set.
        """
        if self._scope_initialized:
            return

        if self._config.has_scope():
            self._scope_initialized = True
            return

        await self._fetch_and_set_scope_async()
        self._scope_initialized = True

    def _fetch_and_set_scope(self) -> None:
        """Fetch and set the project/environment scope from the API key."""
        import logging
        logger = logging.getLogger("permissio")

        url = f"{self._config.api_url}/v1/api-key/scope"
        try:
            response = self._base_client.request("GET", url)
            data = response.json()
            project_id = data.get("project_id")
            environment_id = data.get("environment_id")

            if project_id and environment_id:
                self._config.update_scope(project_id, environment_id)
                if self._config.debug:
                    logger.debug(f"Auto-fetched scope: project_id={project_id}, environment_id={environment_id}")
            else:
                raise ValueError(
                    "Failed to fetch API key scope. "
                    "Either provide project_id and environment_id in config, "
                    "or ensure the API key has valid scope."
                )
        except Exception as e:
            if not self._config.has_scope():
                raise ValueError(
                    f"Failed to fetch API key scope: {e}. "
                    "Either provide project_id and environment_id in config, "
                    "or ensure the API key has valid scope."
                ) from e

    async def _fetch_and_set_scope_async(self) -> None:
        """Fetch and set the project/environment scope from the API key (async)."""
        import logging
        logger = logging.getLogger("permissio")

        url = f"{self._config.api_url}/v1/api-key/scope"
        try:
            response = await self._base_client.request_async("GET", url)
            data = response.json()
            project_id = data.get("project_id")
            environment_id = data.get("environment_id")

            if project_id and environment_id:
                self._config.update_scope(project_id, environment_id)
                if self._config.debug:
                    logger.debug(f"Auto-fetched scope: project_id={project_id}, environment_id={environment_id}")
            else:
                raise ValueError(
                    "Failed to fetch API key scope. "
                    "Either provide project_id and environment_id in config, "
                    "or ensure the API key has valid scope."
                )
        except Exception as e:
            if not self._config.has_scope():
                raise ValueError(
                    f"Failed to fetch API key scope: {e}. "
                    "Either provide project_id and environment_id in config, "
                    "or ensure the API key has valid scope."
                ) from e

    @property
    def config(self) -> PermissioConfig:
        """Get the SDK configuration."""
        return self._config

    @property
    def api(self) -> PermissioApi:
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
            allowed = permissio.check("user@example.com", "read", "document")

            # With tenant
            allowed = permissio.check("user@example.com", "read", "document", tenant="acme")

            # With resource instance
            allowed = permissio.check(
                "user@example.com",
                "read",
                {"type": "document", "key": "doc-123"}
            )

            # With ABAC
            allowed = permissio.check(
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

        This performs client-side permission checking by:
        1. Fetching user's role assignments
        2. Fetching role definitions with permissions
        3. Checking if any role grants the required permission

        Args:
            user: User identifier (key, dict with attributes, or CheckUser).
            action: Action to check permission for.
            resource: Resource to check (type, dict with attributes, or CheckResource).
            tenant: Tenant key (optional, can also be specified in resource).
            context: Additional context for the check.

        Returns:
            CheckResponse with allowed status and additional details.
        """
        import logging
        logger = logging.getLogger("permissio")

        # Normalize inputs
        user_data = normalize_user(user)
        resource_data = normalize_resource(resource)

        # Extract user key and resource type
        user_key = user_data.get("key", "")
        resource_type = resource_data.get("type", "")
        tenant_key = tenant or resource_data.get("tenant")

        # Build required permission string
        required_permission = f"{resource_type}:{action}"

        if self._config.debug:
            logger.debug(f"Permission check: user={user_key}, action={action}, resource={resource_type}, permission={required_permission}")

        # 1. Get user's role assignments
        try:
            assignments = self._api.users.get_roles(user_key, tenant=tenant_key)
        except Exception as e:
            return CheckResponse(
                allowed=False,
                reason=f"Error fetching role assignments: {e}",
            )

        if not assignments:
            return CheckResponse(
                allowed=False,
                reason=f"User {user_key} has no role assignments",
            )

        # 2. Get unique role keys from assignments
        role_keys = set(a.role for a in assignments)

        if self._config.debug:
            logger.debug(f"User's role keys: {list(role_keys)}")

        # 3. Fetch all roles and build permission map
        try:
            roles_response = self._api.roles.list(per_page=100)
        except Exception as e:
            return CheckResponse(
                allowed=False,
                reason=f"Error fetching roles: {e}",
            )

        roles_map = {role.key: role for role in roles_response.data}

        # 4. Check if any assigned role grants the required permission
        matched_roles = []

        for role_key in role_keys:
            permissions = self._get_role_permissions(role_key, roles_map, set())

            if self._config.debug:
                logger.debug(f"Role {role_key} permissions: {permissions}")

            for perm in permissions:
                if (perm == required_permission or
                    perm == f"{resource_type}:*" or
                    perm == "*:*"):
                    matched_roles.append(role_key)
                    break

        allowed = len(matched_roles) > 0

        if allowed:
            reason = f"Granted by role(s): {', '.join(matched_roles)}"
        else:
            reason = f"No role grants permission {required_permission}"

        return CheckResponse(
            allowed=allowed,
            reason=reason,
            matched_roles=matched_roles,
        )

    def _get_role_permissions(
        self,
        role_key: str,
        roles_map: Dict[str, Any],
        visited: set,
    ) -> list:
        """
        Get all permissions for a role, including inherited permissions.

        Args:
            role_key: The role key.
            roles_map: Map of role keys to role objects.
            visited: Set of already visited role keys (for cycle detection).

        Returns:
            List of permission strings.
        """
        if role_key in visited:
            return []

        visited.add(role_key)
        role = roles_map.get(role_key)
        if not role:
            return []

        permissions = list(role.permissions) if role.permissions else []

        # Handle role inheritance (extends)
        if role.extends:
            for parent_key in role.extends:
                parent_permissions = self._get_role_permissions(parent_key, roles_map, visited)
                permissions.extend(parent_permissions)

        return permissions

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

        This performs client-side permission checking by:
        1. Fetching user's role assignments
        2. Fetching role definitions with permissions
        3. Checking if any role grants the required permission

        Args:
            user: User identifier (key, dict with attributes, or CheckUser).
            action: Action to check permission for.
            resource: Resource to check (type, dict with attributes, or CheckResource).
            tenant: Tenant key (optional, can also be specified in resource).
            context: Additional context for the check.

        Returns:
            CheckResponse with allowed status and additional details.
        """
        import logging
        logger = logging.getLogger("permissio")

        # Normalize inputs
        user_data = normalize_user(user)
        resource_data = normalize_resource(resource)

        # Extract user key and resource type
        user_key = user_data.get("key", "")
        resource_type = resource_data.get("type", "")
        tenant_key = tenant or resource_data.get("tenant")

        # Build required permission string
        required_permission = f"{resource_type}:{action}"

        if self._config.debug:
            logger.debug(f"Permission check: user={user_key}, action={action}, resource={resource_type}, permission={required_permission}")

        # 1. Get user's role assignments
        try:
            assignments = await self._api.users.get_roles_async(user_key, tenant=tenant_key)
        except Exception as e:
            return CheckResponse(
                allowed=False,
                reason=f"Error fetching role assignments: {e}",
            )

        if not assignments:
            return CheckResponse(
                allowed=False,
                reason=f"User {user_key} has no role assignments",
            )

        # 2. Get unique role keys from assignments
        role_keys = set(a.role for a in assignments)

        if self._config.debug:
            logger.debug(f"User's role keys: {list(role_keys)}")

        # 3. Fetch all roles and build permission map
        try:
            roles_response = await self._api.roles.list_async(per_page=100)
        except Exception as e:
            return CheckResponse(
                allowed=False,
                reason=f"Error fetching roles: {e}",
            )

        roles_map = {role.key: role for role in roles_response.data}

        # 4. Check if any assigned role grants the required permission
        matched_roles = []

        for role_key in role_keys:
            permissions = self._get_role_permissions(role_key, roles_map, set())

            if self._config.debug:
                logger.debug(f"Role {role_key} permissions: {permissions}")

            for perm in permissions:
                if (perm == required_permission or
                    perm == f"{resource_type}:*" or
                    perm == "*:*"):
                    matched_roles.append(role_key)
                    break

        allowed = len(matched_roles) > 0

        if allowed:
            reason = f"Granted by role(s): {', '.join(matched_roles)}"
        else:
            reason = f"No role grants permission {required_permission}"

        return CheckResponse(
            allowed=allowed,
            reason=reason,
            matched_roles=matched_roles,
        )

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
            results = permissio.bulk_check([
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

    def __enter__(self) -> "Permissio":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    async def __aenter__(self) -> "Permissio":
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
