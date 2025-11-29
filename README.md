# Permissio.io Python SDK

Official Python SDK for the [Permissio.io](https://permissio.io) authorization platform.

## Installation

```bash
pip install permisio
```

## Quick Start

```python
from permissio import Permissio

# Initialize the client
permissio = Permissio(
    token="permis_key_your_api_key",
    project_id="your-project-id",
    environment_id="your-environment-id",
)

# Check permission
if permissio.check("user@example.com", "read", "document"):
    print("Access granted!")
else:
    print("Access denied!")
```

## Synchronous Usage

For synchronous-first usage (similar to Permit.io SDK):

```python
from permissio.sync import Permissio

permissio = Permissio(
    token="permis_key_your_api_key",
    project_id="your-project-id",
    environment_id="your-environment-id",
)

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

For async applications:

```python
import asyncio
from permissio import Permissio

async def main():
    permissio = Permissio(
        token="permis_key_your_api_key",
        project_id="your-project-id",
        environment_id="your-environment-id",
    )

    # Async permission check
    allowed = await permissio.check_async("user@example.com", "read", "document")
    
    # Close the client when done
    await permissio.close_async()

asyncio.run(main())
```

## ABAC (Attribute-Based Access Control)

```python
from permissio import Permissio
from permissio.enforcement import UserBuilder, ResourceBuilder

permissio = Permissio(token="permis_key_your_api_key")

# Build user with attributes
user = (
    UserBuilder("user@example.com")
    .with_attribute("department", "engineering")
    .with_attribute("level", 5)
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

# Check with ABAC
allowed = permissio.check(user, "read", resource)
```

## API Usage

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
```

### Tenants

```python
from permissio.models import TenantCreate

# List tenants
tenants = permissio.api.tenants.list()

# Create a tenant
tenant = permissio.api.tenants.create(TenantCreate(
    key="acme-corp",
    name="Acme Corporation",
))

# Get a tenant
tenant = permissio.api.tenants.get("acme-corp")
```

### Roles

```python
from permissio.models import RoleCreate

# List roles
roles = permissio.api.roles.list()

# Create a role
role = permissio.api.roles.create(RoleCreate(
    key="editor",
    name="Editor",
    permissions=["document:read", "document:write"],
))
```

### Role Assignments

```python
# Assign a role to a user
permissio.api.role_assignments.assign(
    user="user@example.com",
    role="editor",
    tenant="acme-corp",
)

# Or use convenience method
permissio.assign_role("user@example.com", "editor", tenant="acme-corp")

# Unassign a role
permissio.unassign_role("user@example.com", "editor", tenant="acme-corp")

# List role assignments
assignments = permissio.api.role_assignments.list(user="user@example.com")
```

### Resources

```python
from permissio.models import ResourceCreate, ResourceAction

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

# List resources
resources = permissio.api.resources.list()
```

## Configuration

### Using ConfigBuilder

```python
from permissio import ConfigBuilder

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
| `project_id` | str | None | Project identifier |
| `environment_id` | str | None | Environment identifier |
| `timeout` | float | 30.0 | Request timeout in seconds |
| `debug` | bool | False | Enable debug logging |
| `retry_attempts` | int | 3 | Number of retry attempts |
| `throw_on_error` | bool | True | Raise exceptions on errors |
| `custom_headers` | dict | {} | Additional HTTP headers |

## Error Handling

```python
from permissio.errors import (
    PermisError,
    PermisApiError,
    PermisNotFoundError,
    PermisAuthenticationError,
)

try:
    user = permissio.api.users.get("nonexistent@example.com")
except PermisNotFoundError as e:
    print(f"User not found: {e.message}")
except PermisAuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except PermisApiError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
except PermisError as e:
    print(f"SDK error: {e.message}")
```

## Context Manager

```python
# Automatically closes the client
with Permis(token="permis_key_your_api_key") as permis:
    allowed = permissio.check("user@example.com", "read", "document")

# Async context manager
async with Permis(token="permis_key_your_api_key") as permis:
    allowed = await permissio.check_async("user@example.com", "read", "document")
```

## Flask Integration

```python
from flask import Flask, g, request
from permissio import Permissio

app = Flask(__name__)
permissio = Permissio(
    token="permis_key_your_api_key",
    project_id="your-project-id",
    environment_id="your-environment-id",
)

def require_permission(action: str, resource: str):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = g.user.id  # Get from your auth system
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
