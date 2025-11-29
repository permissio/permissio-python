"""
Async example for the Permis.io Python SDK.

This example demonstrates:
- Async client usage
- Async permission checks
- Async API operations
- Integration with asyncio
"""

import asyncio

from permisio import Permis
from permisio.enforcement import UserBuilder, ResourceBuilder
from permisio.models import UserCreate, TenantCreate
from permisio.errors import PermisApiError


async def main():
    # =========================================================================
    # Async Client Initialization
    # =========================================================================
    
    print("=== Async Client Example ===\n")
    
    # Initialize the client (works for both sync and async)
    permis = Permis(
        token="permis_key_your_api_key_here",
        project_id="my-project",
        environment_id="production",
    )
    
    try:
        # =====================================================================
        # Async Permission Checks
        # =====================================================================
        
        print("--- Permission Checks ---")
        
        # Simple async check
        allowed = await permis.check_async("user@example.com", "read", "document")
        print(f"Can user read document? {allowed}")
        
        # Check with ABAC
        user = (
            UserBuilder("user@example.com")
            .with_attribute("department", "engineering")
            .build()
        )
        
        resource = (
            ResourceBuilder("document")
            .with_key("doc-123")
            .with_tenant("acme-corp")
            .build()
        )
        
        allowed = await permis.check_async(user, "read", resource)
        print(f"Can engineering user read doc-123? {allowed}")
        
        # Get detailed response
        response = await permis.check_with_details_async(
            "user@example.com", "write", "document"
        )
        print(f"Write allowed: {response.allowed}")
        
        # =====================================================================
        # Concurrent Permission Checks
        # =====================================================================
        
        print("\n--- Concurrent Permission Checks ---")
        
        # Check multiple permissions concurrently
        checks = [
            permis.check_async("user1@example.com", "read", "document"),
            permis.check_async("user2@example.com", "read", "document"),
            permis.check_async("user1@example.com", "write", "document"),
            permis.check_async("user2@example.com", "delete", "document"),
        ]
        
        results = await asyncio.gather(*checks)
        
        check_descriptions = [
            "user1 read document",
            "user2 read document",
            "user1 write document",
            "user2 delete document",
        ]
        
        for desc, result in zip(check_descriptions, results):
            print(f"  {desc}: {result}")
        
        # =====================================================================
        # Async API Operations
        # =====================================================================
        
        print("\n--- Async API Operations ---")
        
        try:
            # List users async
            users = await permis.api.users.list_async(page=1, per_page=5)
            print(f"Total users: {users.pagination.total}")
            
            # Create user async
            new_user = await permis.api.users.create_async(UserCreate(
                key="async.user@example.com",
                email="async.user@example.com",
                first_name="Async",
                last_name="User",
            ))
            print(f"Created user: {new_user.key}")
            
            # Get user async
            user = await permis.api.users.get_async("async.user@example.com")
            print(f"Got user: {user.key}")
            
            # Delete user async
            await permis.api.users.delete_async("async.user@example.com")
            print("Deleted user")
            
        except PermisApiError as e:
            print(f"API error: {e.message}")
        
        # =====================================================================
        # Async Role Assignment
        # =====================================================================
        
        print("\n--- Async Role Assignment ---")
        
        try:
            # Assign role async
            assignment = await permis.api.role_assignments.assign_async(
                user="user@example.com",
                role="viewer",
                tenant="acme-corp",
            )
            print(f"Assigned role: {assignment.role_key}")
            
            # List assignments async
            assignments = await permis.api.role_assignments.list_async(
                user="user@example.com"
            )
            print(f"User has {len(assignments.data)} role assignments")
            
            # Unassign role async
            await permis.api.role_assignments.unassign_async(
                user="user@example.com",
                role="viewer",
                tenant="acme-corp",
            )
            print("Unassigned role")
            
        except PermisApiError as e:
            print(f"API error: {e.message}")
        
        # =====================================================================
        # Parallel API Operations
        # =====================================================================
        
        print("\n--- Parallel API Operations ---")
        
        # Fetch multiple resources concurrently
        try:
            users_task = permis.api.users.list_async()
            tenants_task = permis.api.tenants.list_async()
            roles_task = permis.api.roles.list_async()
            resources_task = permis.api.resources.list_async()
            
            users, tenants, roles, resources = await asyncio.gather(
                users_task, tenants_task, roles_task, resources_task
            )
            
            print(f"  Users: {users.pagination.total}")
            print(f"  Tenants: {tenants.pagination.total}")
            print(f"  Roles: {roles.pagination.total}")
            print(f"  Resources: {resources.pagination.total}")
            
        except PermisApiError as e:
            print(f"API error: {e.message}")
        
    finally:
        # =====================================================================
        # Cleanup
        # =====================================================================
        
        print("\n--- Cleanup ---")
        await permis.close_async()
        print("Client closed")


async def context_manager_example():
    """Example using async context manager."""
    
    print("\n=== Context Manager Example ===")
    
    async with Permis(token="permis_key_your_api_key") as permis:
        allowed = await permis.check_async("user@example.com", "read", "document")
        print(f"Permission check result: {allowed}")
    
    print("Client automatically closed")


async def batch_operations_example():
    """Example of batch operations."""
    
    print("\n=== Batch Operations Example ===")
    
    permis = Permis(token="permis_key_your_api_key")
    
    try:
        # Create multiple users concurrently
        user_creates = [
            permis.api.users.create_async(UserCreate(
                key=f"batch.user{i}@example.com",
                email=f"batch.user{i}@example.com",
            ))
            for i in range(5)
        ]
        
        created_users = await asyncio.gather(*user_creates, return_exceptions=True)
        
        successful = [u for u in created_users if not isinstance(u, Exception)]
        failed = [u for u in created_users if isinstance(u, Exception)]
        
        print(f"Created {len(successful)} users, {len(failed)} failed")
        
        # Clean up - delete created users
        delete_tasks = [
            permis.api.users.delete_async(f"batch.user{i}@example.com")
            for i in range(5)
        ]
        
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        print("Cleaned up batch users")
        
    finally:
        await permis.close_async()


if __name__ == "__main__":
    # Run main example
    asyncio.run(main())
    
    # Run additional examples
    asyncio.run(context_manager_example())
    asyncio.run(batch_operations_example())
