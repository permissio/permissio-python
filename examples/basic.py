"""
Basic usage example for the Permis.io Python SDK.

This example demonstrates:
- Client initialization
- Permission checks
- Using enforcement builders
- API operations for users, tenants, and roles
"""

from permisio import Permis, ConfigBuilder
from permisio.enforcement import UserBuilder, ResourceBuilder
from permisio.models import UserCreate, TenantCreate, RoleCreate
from permisio.errors import PermisApiError, PermisNotFoundError


def main():
    # =========================================================================
    # Client Initialization
    # =========================================================================
    
    # Option 1: Simple initialization
    permis = Permis(
        token="permis_key_your_api_key_here",
        project_id="my-project",
        environment_id="production",
    )
    
    # Option 2: Using ConfigBuilder
    config = (
        ConfigBuilder("permis_key_your_api_key_here")
        .with_project_id("my-project")
        .with_environment_id("production")
        .with_debug(True)
        .with_timeout(30.0)
        .build()
    )
    permis = Permis(config=config)
    
    # =========================================================================
    # Simple Permission Check
    # =========================================================================
    
    print("=== Simple Permission Check ===")
    
    # Check if user can read a document
    allowed = permis.check("user@example.com", "read", "document")
    print(f"Can user read document? {allowed}")
    
    # Check with tenant context
    allowed = permis.check(
        "user@example.com",
        "write",
        "document",
        tenant="acme-corp"
    )
    print(f"Can user write document in acme-corp? {allowed}")
    
    # Check with resource instance
    allowed = permis.check(
        "user@example.com",
        "delete",
        {"type": "document", "key": "doc-123"}
    )
    print(f"Can user delete doc-123? {allowed}")
    
    # =========================================================================
    # ABAC Permission Check
    # =========================================================================
    
    print("\n=== ABAC Permission Check ===")
    
    # Build user with attributes
    user = (
        UserBuilder("user@example.com")
        .with_attribute("department", "engineering")
        .with_attribute("level", 5)
        .with_attribute("location", "US")
        .build()
    )
    
    # Build resource with attributes
    resource = (
        ResourceBuilder("document")
        .with_key("doc-confidential-123")
        .with_tenant("acme-corp")
        .with_attribute("classification", "confidential")
        .with_attribute("owner_department", "engineering")
        .build()
    )
    
    # Check permission with ABAC
    allowed = permis.check(user, "read", resource)
    print(f"Can engineering user (level 5) read confidential doc? {allowed}")
    
    # Get detailed response
    response = permis.check_with_details(user, "read", resource)
    print(f"Allowed: {response.allowed}")
    if response.reason:
        print(f"Reason: {response.reason}")
    
    # =========================================================================
    # Bulk Permission Check
    # =========================================================================
    
    print("\n=== Bulk Permission Check ===")
    
    checks = [
        {"user": "user1@example.com", "action": "read", "resource": "document"},
        {"user": "user1@example.com", "action": "write", "resource": "document"},
        {"user": "user2@example.com", "action": "read", "resource": "document"},
        {"user": "user2@example.com", "action": "delete", "resource": "document"},
    ]
    
    results = permis.bulk_check(checks)
    for i, result in enumerate(results.results):
        check = checks[i]
        print(f"{check['user']} can {check['action']} {check['resource']}: {result.allowed}")
    
    print(f"All allowed: {results.all_allowed()}")
    print(f"Any allowed: {results.any_allowed()}")
    
    # =========================================================================
    # User Management
    # =========================================================================
    
    print("\n=== User Management ===")
    
    try:
        # Create a user
        new_user = permis.api.users.create(UserCreate(
            key="new.user@example.com",
            email="new.user@example.com",
            first_name="New",
            last_name="User",
            attributes={"department": "sales"},
        ))
        print(f"Created user: {new_user.key}")
        
        # List users
        users = permis.api.users.list(page=1, per_page=10)
        print(f"Total users: {users.pagination.total}")
        for user in users.data:
            print(f"  - {user.key}")
        
        # Get a specific user
        user = permis.api.users.get("new.user@example.com")
        print(f"Got user: {user.key} ({user.email})")
        
        # Delete the user
        permis.api.users.delete("new.user@example.com")
        print("Deleted user")
        
    except PermisNotFoundError as e:
        print(f"User not found: {e.message}")
    except PermisApiError as e:
        print(f"API error: {e.message}")
    
    # =========================================================================
    # Tenant Management
    # =========================================================================
    
    print("\n=== Tenant Management ===")
    
    try:
        # Create a tenant
        tenant = permis.api.tenants.create(TenantCreate(
            key="demo-tenant",
            name="Demo Tenant",
            description="A demo tenant for testing",
        ))
        print(f"Created tenant: {tenant.key}")
        
        # Or use convenience method
        tenant2 = permis.create_tenant({
            "key": "demo-tenant-2",
            "name": "Demo Tenant 2",
        })
        print(f"Created tenant: {tenant2.key}")
        
        # List tenants
        tenants = permis.api.tenants.list()
        print(f"Total tenants: {tenants.pagination.total}")
        
    except PermisApiError as e:
        print(f"API error: {e.message}")
    
    # =========================================================================
    # Role Management
    # =========================================================================
    
    print("\n=== Role Management ===")
    
    try:
        # Create a role
        role = permis.api.roles.create(RoleCreate(
            key="editor",
            name="Editor",
            description="Can read and write documents",
            permissions=["document:read", "document:write"],
        ))
        print(f"Created role: {role.key}")
        
        # List roles
        roles = permis.api.roles.list()
        print(f"Total roles: {roles.pagination.total}")
        for role in roles.data:
            print(f"  - {role.key}: {role.permissions}")
        
    except PermisApiError as e:
        print(f"API error: {e.message}")
    
    # =========================================================================
    # Role Assignment
    # =========================================================================
    
    print("\n=== Role Assignment ===")
    
    try:
        # Assign a role to a user
        assignment = permis.assign_role(
            user="user@example.com",
            role="editor",
            tenant="acme-corp",
        )
        print(f"Assigned role: {assignment.role_key} to {assignment.user_key}")
        
        # Get user's roles
        roles = permis.api.users.get_roles("user@example.com")
        print(f"User roles: {[r.role_key for r in roles]}")
        
        # Unassign the role
        permis.unassign_role(
            user="user@example.com",
            role="editor",
            tenant="acme-corp",
        )
        print("Unassigned role")
        
    except PermisApiError as e:
        print(f"API error: {e.message}")
    
    # =========================================================================
    # Sync User (Create or Update with Roles)
    # =========================================================================
    
    print("\n=== Sync User ===")
    
    try:
        # Sync a user with roles
        synced_user = permis.sync_user({
            "key": "synced.user@example.com",
            "email": "synced.user@example.com",
            "first_name": "Synced",
            "last_name": "User",
            "roles": [
                {"role": "viewer", "tenant": "acme-corp"},
                {"role": "editor", "tenant": "demo-tenant"},
            ],
        })
        print(f"Synced user: {synced_user.key}")
        
    except PermisApiError as e:
        print(f"API error: {e.message}")
    
    # =========================================================================
    # Cleanup
    # =========================================================================
    
    print("\n=== Cleanup ===")
    permis.close()
    print("Client closed")


if __name__ == "__main__":
    main()
