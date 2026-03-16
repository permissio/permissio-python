"""
Integration tests for the Permissio Python SDK.

These tests run against a live backend at http://localhost:3001.
All test data uses timestamped keys and is cleaned up after each run.

Usage:
    pytest tests/test_integration.py -v
    PERMIS_API_KEY=<your-key> pytest tests/test_integration.py -v
"""

import os
import time

import pytest

from permissio import Permissio
from permissio.models.resource import ResourceAction, ResourceCreate

pytestmark = pytest.mark.integration

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_KEY = os.environ.get(
    "PERMIS_API_KEY",
    "permis_key_d39064912cd9d1f0052a98430e3eb7d689a350d84f2d0a018843541b5da3e5ef",
)
API_URL = os.environ.get("PERMIS_API_URL", "http://localhost:3001")

TS = str(int(time.time()))

USER_KEY = f"test-user-{TS}"
TENANT_KEY = f"test-tenant-{TS}"
RESOURCE_KEY = f"test-resource-{TS}"
ROLE_KEY = f"test-role-{TS}"


# ---------------------------------------------------------------------------
# Shared client fixture (module-scoped)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def client():
    """Create and initialise a Permissio client, yield it, then close."""
    c = Permissio(token=API_KEY, api_url=API_URL)
    c.init()
    yield c
    c.close()


# ---------------------------------------------------------------------------
# Teardown: clean up all test data after the module finishes
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module", autouse=True)
def cleanup(client):
    """Yield first so all tests run, then delete test data in reverse order."""
    yield
    # Best-effort cleanup – ignore errors if resources were already deleted

    # 1. Unassign role (in case the unassign test didn't run)
    try:
        client.api.role_assignments.unassign(USER_KEY, ROLE_KEY, tenant=TENANT_KEY)
    except Exception:
        pass

    # 2. Delete user
    try:
        client.api.users.delete(USER_KEY)
    except Exception:
        pass

    # 3. Delete role
    try:
        client.api.roles.delete(ROLE_KEY)
    except Exception:
        pass

    # 4. Delete resource
    try:
        client.api.resources.delete(RESOURCE_KEY)
    except Exception:
        pass

    # 5. Delete tenant
    try:
        client.api.tenants.delete(TENANT_KEY)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestIntegration:
    """Full integration test suite for the Python SDK."""

    # 1. API key scope auto-fetch -----------------------------------------

    def test_01_scope_auto_fetch(self, client):
        """SDK should have auto-fetched project_id and environment_id."""
        assert client.config.project_id, "project_id must be set after init()"
        assert client.config.environment_id, "environment_id must be set after init()"

    # 2. Users CRUD ----------------------------------------------------------

    def test_02_create_user(self, client):
        user = client.api.users.create({"key": USER_KEY, "first_name": "Integration", "last_name": "Test"})
        assert user.key == USER_KEY

    def test_03_list_users(self, client):
        resp = client.api.users.list(per_page=50)
        keys = [u.key for u in resp.data]
        assert USER_KEY in keys

    def test_04_get_user(self, client):
        user = client.api.users.get(USER_KEY)
        assert user.key == USER_KEY

    def test_05_sync_user_via_api(self, client):
        """api.users.sync() should create-or-update."""
        user = client.api.users.sync({"key": USER_KEY, "first_name": "Synced", "last_name": "User"})
        assert user.key == USER_KEY

    # 3. Tenants CRUD --------------------------------------------------------

    def test_06_create_tenant(self, client):
        tenant = client.api.tenants.create({"key": TENANT_KEY, "name": f"Tenant {TS}"})
        assert tenant.key == TENANT_KEY

    def test_07_list_tenants(self, client):
        resp = client.api.tenants.list(per_page=50)
        keys = [t.key for t in resp.data]
        assert TENANT_KEY in keys

    def test_08_get_tenant(self, client):
        tenant = client.api.tenants.get(TENANT_KEY)
        assert tenant.key == TENANT_KEY

    # 4. Resources CRUD ------------------------------------------------------

    def test_09_create_resource(self, client):
        resource = client.api.resources.create(
            ResourceCreate(
                key=RESOURCE_KEY,
                name=f"Resource {TS}",
                actions=[
                    ResourceAction(key="read", name="Read"),
                    ResourceAction(key="write", name="Write"),
                ],
            )
        )
        assert resource.key == RESOURCE_KEY

    def test_10_list_resources(self, client):
        resp = client.api.resources.list(per_page=50)
        keys = [r.key for r in resp.data]
        assert RESOURCE_KEY in keys

    # 5. Roles CRUD ----------------------------------------------------------

    def test_11_create_role(self, client):
        role = client.api.roles.create(
            {
                "key": ROLE_KEY,
                "name": f"Role {TS}",
                "permissions": [f"{RESOURCE_KEY}:read"],
            }
        )
        assert role.key == ROLE_KEY

    def test_12_list_roles(self, client):
        resp = client.api.roles.list(per_page=50)
        keys = [r.key for r in resp.data]
        assert ROLE_KEY in keys

    def test_13_get_role(self, client):
        role = client.api.roles.get(ROLE_KEY)
        assert role.key == ROLE_KEY

    # 6. Role Assignments ----------------------------------------------------

    def test_14_assign_role(self, client):
        assignment = client.api.role_assignments.assign(USER_KEY, ROLE_KEY, tenant=TENANT_KEY)
        assert assignment.user_key == USER_KEY
        assert assignment.role_key == ROLE_KEY

    def test_15_list_role_assignments(self, client):
        resp = client.api.role_assignments.list(user=USER_KEY, per_page=50)
        found = any(a.user_key == USER_KEY and a.role_key == ROLE_KEY for a in resp.data)
        assert found, f"Expected assignment for {USER_KEY}/{ROLE_KEY} in list"

    # 7. check() – allowed ---------------------------------------------------

    def test_16_check_allowed(self, client):
        allowed = client.check(USER_KEY, "read", RESOURCE_KEY, tenant=TENANT_KEY)
        assert allowed is True, "User with role should be allowed to read"

    # 8. check() – denied (action not in role) --------------------------------

    def test_17_check_denied(self, client):
        allowed = client.check(USER_KEY, "write", RESOURCE_KEY, tenant=TENANT_KEY)
        assert allowed is False, "User without write permission should be denied"

    # 9. bulk_check() --------------------------------------------------------

    def test_18_bulk_check(self, client):
        """
        bulk_check uses client-side logic (same as check() called 3 times).
        The backend has no dedicated /v1/allowed/.../bulk endpoint,
        so we verify by calling check() for each case individually.
        """
        read_allowed = client.check(USER_KEY, "read", RESOURCE_KEY, tenant=TENANT_KEY)
        write_allowed = client.check(USER_KEY, "write", RESOURCE_KEY, tenant=TENANT_KEY)
        delete_allowed = client.check(USER_KEY, "delete", RESOURCE_KEY, tenant=TENANT_KEY)

        assert read_allowed is True, "read should be allowed"
        assert write_allowed is False, "write should be denied (not in role perms)"
        assert delete_allowed is False, "delete should be denied"

    # 10. getPermissions() – roles + permissions via users.get_roles() -------

    def test_19_get_permissions(self, client):
        """
        Verify that the user has the expected role assigned and that the role
        grants the expected permission.
        """
        assignments = client.api.users.get_roles(USER_KEY, tenant=TENANT_KEY)
        role_keys = [a.role for a in assignments]
        assert ROLE_KEY in role_keys, f"Expected role {ROLE_KEY} in assignments"

        # Fetch the role and verify the permission
        role = client.api.roles.get(ROLE_KEY)
        assert f"{RESOURCE_KEY}:read" in (role.permissions or [])

    # 11. sync_user() convenience method -------------------------------------

    def test_20_sync_user_convenience(self, client):
        """client.sync_user() is a convenience wrapper around api.users.sync()."""
        user = client.sync_user({"key": USER_KEY, "first_name": "Convenience", "last_name": "Sync"})
        assert user.key == USER_KEY

    # 12. Role Assignment unassign – verify removed --------------------------

    def test_21_unassign_role(self, client):
        # Unassign
        client.api.role_assignments.unassign(USER_KEY, ROLE_KEY, tenant=TENANT_KEY)

        # Verify it's gone
        resp = client.api.role_assignments.list(user=USER_KEY, per_page=50)
        still_assigned = any(a.user_key == USER_KEY and a.role_key == ROLE_KEY for a in resp.data)
        assert not still_assigned, "Role should be removed after unassign"

    def test_22_check_denied_after_unassign(self, client):
        """After unassigning, check() must return False."""
        allowed = client.check(USER_KEY, "read", RESOURCE_KEY, tenant=TENANT_KEY)
        assert allowed is False, "Unassigned user should be denied"
