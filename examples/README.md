# Examples

This directory contains example code demonstrating how to use the Permissio.io Python SDK.

## Examples

### [basic.py](./basic.py)

Basic usage examples including:
- Client initialization (simple and ConfigBuilder)
- Simple permission checks
- ABAC permission checks with user/resource builders
- Bulk permission checks
- User, Tenant, and Role management
- Role assignment operations
- User sync functionality

```bash
python examples/basic.py
```

### [async_example.py](./async_example.py)

Async/await examples including:
- Async permission checks
- Concurrent permission checks with `asyncio.gather()`
- Async API operations
- Parallel API operations
- Context manager usage
- Batch operations

```bash
python examples/async_example.py
```

### [flask_example.py](./flask_example.py)

Flask web framework integration including:
- Permission decorator (`@require_permission`)
- Multi-permission decorators (`@require_any_permission`, `@require_all_permissions`)
- Authentication middleware integration
- Helper functions for templates (`can_user()`)
- User sync endpoint
- Error handlers

```bash
# Install Flask first
pip install flask

# Run the example
python examples/flask_example.py

# Test with curl
curl http://localhost:5000/
curl -H "Authorization: Bearer user123" http://localhost:5000/documents
curl -H "Authorization: Bearer user123" http://localhost:5000/documents/doc-1
```

## Running the Examples

1. Install the SDK:
   ```bash
   pip install permisio
   # or for development
   pip install -e .
   ```

2. Set your API key:
   ```bash
   export PERMIS_API_KEY="permis_key_your_api_key_here"
   ```

3. Run an example:
   ```bash
   python examples/basic.py
   ```

## Configuration

All examples use placeholder values for:
- `token`: Replace with your actual API key
- `project_id`: Replace with your project ID
- `environment_id`: Replace with your environment ID

For production use, load these from environment variables:

```python
import os
from permisio import Permis

permis = Permis(
    token=os.environ["PERMIS_API_KEY"],
    project_id=os.environ["PERMIS_PROJECT_ID"],
    environment_id=os.environ["PERMIS_ENVIRONMENT_ID"],
)
```
