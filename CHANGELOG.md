# Changelog

All notable changes to the Permissio.io Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

No unreleased changes at this time.

---

## [0.1.0-alpha.1] - 2025-03-15

### Added
- **`Permissio` client class**: Main entry point with `token`-based configuration, supporting both sync and async usage patterns
- **`PermissioConfig` dataclass** and **`ConfigBuilder`**: Full configuration support — `token`, `api_url`, `project_id`, `environment_id`, `timeout`, `debug`, `retry_attempts`, `throw_on_error`, `custom_headers`, `http_client`
- **Permission checking (sync)**:
  - `check()` — simple boolean permission check
  - `check_with_details()` — full `CheckResponse` with reason and debug info (client-side RBAC evaluation)
  - `bulk_check()` — batch permission checks
- **Permission checking (async)**:
  - `check_async()` — async boolean permission check
  - `check_with_details_async()` — async full response
  - `bulk_check_async()` — async batch checks
- **Auto-scope detection**: Automatically fetches `project_id` and `environment_id` from the `/v1/api-key/scope` endpoint when not provided
- **Users API** (`api.users`): `list()`, `list_async()`, `get()`, `get_async()`, `create()`, `create_async()`, `update()`, `update_async()`, `delete()`, `delete_async()`, `sync()`, `sync_async()`, `assign_role()`, `assign_role_async()`, `unassign_role()`, `unassign_role_async()`, `get_roles()`, `get_roles_async()`
- **Tenants API** (`api.tenants`): Full sync and async CRUD — `list`, `get`, `create`, `update`, `delete`, plus `sync`
- **Roles API** (`api.roles`): Full sync and async CRUD plus `add_permissions()`, `add_permissions_async()`, `remove_permissions()`, `remove_permissions_async()`
- **Resources API** (`api.resources`): Full sync and async CRUD plus action management (`list_actions`, `create_action`, `delete_action`) and attribute management (`list_attributes`, `create_attribute`, `delete_attribute`)
- **Role Assignments API** (`api.role_assignments`): `list()`, `assign()`, `unassign()`, `bulk_assign()`, `bulk_unassign()`, `list_detailed()` — all with async variants
- **ABAC enforcement builders**:
  - `UserBuilder` — fluent builder for `CheckUser` with attributes, first/last name, email
  - `ResourceBuilder` — fluent builder for `CheckResource` with key, tenant, and attributes
  - `ContextBuilder` — fluent builder for `CheckContext` with arbitrary key/value pairs
- **Convenience methods**: `sync_user()`, `sync_user_async()`, `assign_role()`, `assign_role_async()`, `unassign_role()`, `unassign_role_async()`, `create_tenant()`, `create_tenant_async()`
- **Context manager support**: Both sync (`with Permissio(...) as p:`) and async (`async with Permissio(...) as p:`)
- **`permissio.sync` module**: All classes and types re-exported for sync-first usage patterns
- **Error hierarchy**: `PermissioError` → `PermissioApiError` (with `PermissioRateLimitError`, `PermissioAuthenticationError`, `PermissioPermissionError`, `PermissioNotFoundError`, `PermissioConflictError`), `PermissioNetworkError` → `PermissioTimeoutError`, `PermissioValidationError`
- **Full type hints**: Complete type annotations throughout using Python 3.9+ compatible syntax
- **`httpx` HTTP backend**: Async-first HTTP client with connection pooling and timeout support
- **Examples**: Sync, async, and Flask integration examples
