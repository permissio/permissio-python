# Permissio.io Python SDK

Official Python SDK for the [Permissio.io](https://permissio.io) authorization platform.

## Installation

```bash
pip install permissio
```

## Quick Start

```python
from permissio import Permissio

# Initialize the client (auto-detects project/environment from token)
permissio = Permissio(
    token="permis_key_your_api_key",
)

# Check permission
if permissio.check("user@example.com", "read", "document"):
    print("Access granted!")
else:
    print("Access denied!")
```

If you need to target a specific project and environment, pass them explicitly:

```python
permissio = Permissio(
    token="permis_key_your_api_key",
    project_id="your-project-id",
    environment_id="your-environment-id",
)
```

## Synchronous Usage

For synchronous-first usage, import from `permissio.sync`:

```python
from permissio.sync import Permissio

permissio = Permissio(token="permis_key_your_api_key")

# Simple permission check
allowed = permissio.check("user@example.com", "read", "document")

# Check with tenant
allowed = permissio.check("user@example.com", "read", "document", tenant="acme-corp")

# Check with resource instance
allowed = permissio.check(
    "user@example.com",
    "read",
    {"type": "document", "key": "doc-123"}
)
```

## Async Usage

The default `permissio.Permissio` class exposes async methods alongside sync ones:

```python
import asyncio
from permissio import Permissio

async def main():
    permissio = Permissio(token="permis_key_your_api_key")

    # Async permission check
    allowed = await permissio.check_async("user@example.com", "read", "document")

    # Close the async HTTP client when done
    await permissio.close_async()

asyncio.run(main())
```

> **Note:** Every API method has an `_async` variant (e.g. `permissio.api.users.list_async()`). The sync wrappers in `permissio.sync` call the async variants internally via a managed event loop.

## ABAC (Attribute-Based Access Control)

```python
from permissio import Permissio
from permissio.enforcement import UserBuilder, ResourceBuilder, ContextBuilder

permissio = Permissio(token="permis_key_your_api_key")

# Build user with attributes
user = (
    UserBuilder("user@example.com")
    .with_attribute("department", "engineering")
    .with_attribute("level", 5)
    .with_first_name("Jane")
    .with_last_name("Doe")
    .build()
)

# Build resource with attributes
resource = (
    ResourceBuilder("document")
    .with_key("doc-123")
    .with_tenant("acme-corp")
    .with_attribute("classification", "confidential")
    .build()
)

# Build optional check context
context = (
    ContextBuilder()
    .with_value("ip_address", "192.168.1.1")
    .with_value("request_time", "2026-03-15T12:00:00Z")
    .build()
)

# Check with ABAC + context
allowed = permissio.check(user, "read", resource, context=context)
```

### Enforcement builders

| Class | Description |
|-------|-------------|
| `UserBuilder(key)` | Fluent builder for `CheckUser`; supports `.with_attribute()`, `.with_attributes()`, `.with_first_name()`, `.with_last_name()`, `.with_email()` |
| `ResourceBuilder(type)` | Fluent builder for `CheckResource`; supports `.with_key()`, `.with_tenant()`, `.with_attribute()`, `.with_attributes()` |
| `ContextBuilder()` | Fluent builder for `CheckContext`; supports `.with_value()`, `.with_values()` |

## API Usage

All API methods exist in both sync and async forms. The sync form is the bare name; the async form appends `_async` (e.g. `list()` / `list_async()`).

### Users

```python
from permissio.models import UserCreate, UserUpdate

# List users
users = permissio.api.users.list(page=1, per_page=10)

# Get a user
user = permissio.api.users.get("user@example.com")

# Create a user
new_user = permissio.api.users.create(UserCreate(
    key="new.user@example.com",
    email="new.user@example.com",
    first_name="New",
    last_name="User",
))

# Update a user
updated_user = permissio.api.users.update("user@example.com", UserUpdate(
    first_name="Updated"
))

# Delete a user
permissio.api.users.delete("user@example.com")

# Sync user (upsert) and assign roles
permissio.api.users.sync("user@example.com", roles=["editor"], tenant="acme-corp")

# Assign / unassign a role
permissio.api.users.assign_role("user@example.com", "editor", tenant="acme-corp")
permissio.api.users.unassign_role("user@example.com", "editor", tenant="acme-corp")

# Get tenants for a user
tenants = permissio.api.users.get_tenants("user@example.com")
```

### Tenants

```python
from permissio.models import TenantCreate, TenantUpdate

# List tenants
tenants = permissio.api.tenants.list()

# Get a tenant
tenant = permissio.api.tenants.get("acme-corp")

# Create a tenant
tenant = permissio.api.tenants.create(TenantCreate(
    key="acme-corp",
    name="Acme Corporation",
))

# Update a tenant
tenant = permissio.api.tenants.update("acme-corp", TenantUpdate(name="ACME Corp"))

# Delete a tenant
permissio.api.tenants.delete("acme-corp")

# Sync tenant (upsert)
permissio.api.tenants.sync("acme-corp", name="Acme Corporation")

# Remove a user from a tenant
permissio.api.tenants.remove_user("acme-corp", "user@example.com")
```

### Roles

```python
from permissio.models import RoleCreate, RoleUpdate

# List roles
roles = permissio.api.roles.list()

# Get a role
role = permissio.api.roles.get("editor")

# Create a role
role = permissio.api.roles.create(RoleCreate(
    key="editor",
    name="Editor",
    permissions=["document:read", "document:write"],
))

# Update a role
role = permissio.api.roles.update("editor", RoleUpdate(name="Content Editor"))

# Delete a role
permissio.api.roles.delete("editor")

# Sync role (upsert)
permissio.api.roles.sync("editor", name="Editor", permissions=["document:read"])

# Permission management
permissio.api.roles.add_permission("editor", "document:delete")
permissio.api.roles.remove_permission("editor", "document:delete")
permissions = permissio.api.roles.get_permissions("editor")

# Role inheritance (extends)
permissio.api.roles.add_extends("editor", "viewer")
permissio.api.roles.remove_extends("editor", "viewer")
extends = permissio.api.roles.get_extends("editor")
```

### Resources

```python
from permissio.models import ResourceCreate, ResourceAction, ResourceAttribute

# List resources
resources = permissio.api.resources.list()

# Get a resource
resource = permissio.api.resources.get("document")

# Create a resource type
resource = permissio.api.resources.create(ResourceCreate(
    key="document",
    name="Document",
    actions=[
        ResourceAction(key="read", name="Read"),
        ResourceAction(key="write", name="Write"),
        ResourceAction(key="delete", name="Delete"),
    ],
))

# Update / delete a resource type
permissio.api.resources.update("document", ...)
permissio.api.resources.delete("document")

# Sync resource type (upsert)
permissio.api.resources.sync("document", name="Document")

# Action management
actions = permissio.api.resources.list_actions("document")
permissio.api.resources.create_action("document", ResourceAction(key="share", name="Share"))
permissio.api.resources.delete_action("document", "share")

# Attribute management
attributes = permissio.api.resources.list_attributes("document")
permissio.api.resources.create_attribute("document", ResourceAttribute(key="classification", type="string"))
permissio.api.resources.delete_attribute("document", "classification")
```

### Role Assignments

```python
from permissio.models import RoleAssignmentCreate

# Assign a role to a user
permissio.api.role_assignments.assign(
    user="user@example.com",
    role="editor",
    tenant="acme-corp",
)

# Unassign a role (optionally scoped to a resource instance)
permissio.api.role_assignments.unassign(
    user="user@example.com",
    role="editor",
    tenant="acme-corp",
    resource_instance="document:doc-123",
)

# Convenience methods on the top-level client
permissio.assign_role("user@example.com", "editor", tenant="acme-corp")
permissio.unassign_role("user@example.com", "editor", tenant="acme-corp")

# List role assignments (with filters)
assignments = permissio.api.role_assignments.list(
    user="user@example.com",
    tenant="acme-corp",
)

# List with detailed user/role information
detailed = permissio.api.role_assignments.list_detailed(user="user@example.com")

# Bulk operations
permissio.api.role_assignments.bulk_assign([
    RoleAssignmentCreate(user="alice@example.com", role="editor", tenant="acme-corp"),
    RoleAssignmentCreate(user="bob@example.com", role="viewer", tenant="acme-corp"),
])

permissio.api.role_assignments.bulk_unassign([
    RoleAssignmentCreate(user="alice@example.com", role="editor", tenant="acme-corp"),
])
```

## Configuration

### Using ConfigBuilder

```python
from permissio import ConfigBuilder, Permissio

config = (
    ConfigBuilder("permis_key_your_api_key")
    .with_project_id("your-project-id")
    .with_environment_id("your-environment-id")
    .with_api_url("https://api.permissio.io")
    .with_timeout(30.0)
    .with_retry_attempts(3)
    .with_debug(True)
    .build()
)

permissio = Permissio(config=config)
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `token` | str | (required) | API key starting with `permis_key_` |
| `api_url` | str | `https://api.permissio.io` | Base API URL |
| `project_id` | str | None | Project identifier (auto-detected from token if omitted) |
| `environment_id` | str | None | Environment identifier (auto-detected from token if omitted) |
| `timeout` | float | 30.0 | Request timeout in seconds |
| `debug` | bool | False | Enable debug logging |
| `retry_attempts` | int | 3 | Number of retry attempts |
| `throw_on_error` | bool | True | Raise exceptions on errors |
| `custom_headers` | dict | {} | Additional HTTP headers |

## Error Handling

```python
from permissio.errors import (
    PermissioError,
    PermissioApiError,
    PermissioNotFoundError,
    PermissioAuthenticationError,
    PermissioPermissionError,
    PermissioRateLimitError,
    PermissioNetworkError,
    PermissioTimeoutError,
    PermissioConflictError,
    PermissioValidationError,
)

try:
    user = permissio.api.users.get("nonexistent@example.com")
except PermissioNotFoundError as e:
    print(f"User not found: {e.message}")
except PermissioAuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except PermissioRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except PermissioApiError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
except PermissioError as e:
    print(f"SDK error: {e.message}")
```

### Error hierarchy

```
PermissioError
├── PermissioValidationError
├── PermissioNetworkError
│   └── PermissioTimeoutError
└── PermissioApiError
    ├── PermissioAuthenticationError   (401)
    ├── PermissioPermissionError       (403)
    ├── PermissioNotFoundError         (404)
    ├── PermissioConflictError         (409)
    └── PermissioRateLimitError        (429)
```

`PermissioApiError` exposes convenience properties: `.is_not_found`, `.is_unauthorized`, `.is_forbidden`, `.is_bad_request`, `.is_conflict`, `.is_server_error`, `.is_retryable`.

## Context Manager

```python
# Sync context manager — automatically closes the client
with Permissio(token="permis_key_your_api_key") as permissio:
    allowed = permissio.check("user@example.com", "read", "document")

# Async context manager
async with Permissio(token="permis_key_your_api_key") as permissio:
    allowed = await permissio.check_async("user@example.com", "read", "document")
```

## Flask Integration

```python
from functools import wraps
from flask import Flask, g, abort
from permissio import Permissio

app = Flask(__name__)
permissio = Permissio(token="permis_key_your_api_key")

def require_permission(action: str, resource: str):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = g.user.id  # From your auth system
            if not permissio.check(user_id, action, resource):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route("/documents/<doc_id>")
@require_permission("read", "document")
def get_document(doc_id):
    return {"id": doc_id, "content": "..."}
```

## Requirements

- Python 3.9+
- httpx >= 0.24.0

## License

MIT License - see [LICENSE](LICENSE) for details.

## Documentation

Full documentation is available at [docs.permissio.io/sdk/python](https://docs.permissio.io/sdk/python).
