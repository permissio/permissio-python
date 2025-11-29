"""
Test script to verify the Python SDK works with the local Permissio.io backend.

Before running:
1. Start the backend: cd backend && make docker-dev
2. Create an API key in the UI or use one you have
3. Update the configuration below with your values

Usage:
    python examples/test_local.py
"""

import os
import sys

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from permissio import Permissio, ConfigBuilder
from permissio.models import UserCreate, TenantCreate, RoleCreate
from permissio.errors import PermissioApiError, PermissioNotFoundError


# ============================================================================
# Configuration - UPDATE THESE VALUES
# ============================================================================

# Your API key (get from UI or database)
API_KEY = os.environ.get("PERMIS_API_KEY", "permis_key_your_key_here")

# Your project and environment IDs
PROJECT_ID = os.environ.get("PERMIS_PROJECT_ID", "default")
ENVIRONMENT_ID = os.environ.get("PERMIS_ENVIRONMENT_ID", "development")

# Local backend URL
API_URL = os.environ.get("PERMIS_API_URL", "http://localhost:8080")


def main():
    print("=" * 60)
    print("Permissio.io Python SDK - Local Backend Test")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  API URL: {API_URL}")
    print(f"  Project: {PROJECT_ID}")
    print(f"  Environment: {ENVIRONMENT_ID}")
    print(f"  API Key: {API_KEY[:20]}..." if len(API_KEY) > 20 else f"  API Key: {API_KEY}")
    print()

    # Initialize client - let SDK auto-fetch project/environment from API key
    config = (
        ConfigBuilder(API_KEY)
        .with_api_url(API_URL)
        .with_debug(True)
        .build()
    )
    
    permissio = Permissio(config=config)
    
    # Initialize the SDK to fetch project/environment scope from API key
    try:
        permissio.init()
        print(f"  Auto-fetched Project: {permissio.config.project_id}")
        print(f"  Auto-fetched Environment: {permissio.config.environment_id}")
    except Exception as e:
        print(f"✗ Failed to initialize SDK: {e}")
        return
    
    try:
        # =====================================================================
        # Test 1: List Users
        # =====================================================================
        print("\n--- Test 1: List Users ---")
        try:
            users = permissio.api.users.list(page=1, per_page=5)
            print(f"✓ Found {users.pagination.total} users")
            for user in users.data[:3]:
                print(f"  - {user.key}")
        except PermissioApiError as e:
            print(f"✗ Error: {e.message} (status: {e.status_code})")
        
        # =====================================================================
        # Test 2: List Tenants
        # =====================================================================
        print("\n--- Test 2: List Tenants ---")
        try:
            tenants = permissio.api.tenants.list(page=1, per_page=5)
            print(f"✓ Found {tenants.pagination.total} tenants")
            for tenant in tenants.data[:3]:
                print(f"  - {tenant.key}: {tenant.name}")
        except PermissioApiError as e:
            print(f"✗ Error: {e.message} (status: {e.status_code})")
        
        # =====================================================================
        # Test 3: List Roles
        # =====================================================================
        print("\n--- Test 3: List Roles ---")
        try:
            roles = permissio.api.roles.list(page=1, per_page=5)
            print(f"✓ Found {roles.pagination.total} roles")
            for role in roles.data[:3]:
                print(f"  - {role.key}: {role.name}")
        except PermissioApiError as e:
            print(f"✗ Error: {e.message} (status: {e.status_code})")
        
        # =====================================================================
        # Test 4: List Resources
        # =====================================================================
        print("\n--- Test 4: List Resources ---")
        try:
            resources = permissio.api.resources.list(page=1, per_page=5)
            print(f"✓ Found {resources.pagination.total} resources")
            for resource in resources.data[:3]:
                print(f"  - {resource.key}: {resource.name}")
        except PermissioApiError as e:
            print(f"✗ Error: {e.message} (status: {e.status_code})")
        
        # =====================================================================
        # Test 5: Create and Delete User
        # =====================================================================
        print("\n--- Test 5: Create and Delete User ---")
        test_user_key = "sdk-test-user@example.com"
        try:
            # Create
            new_user = permissio.api.users.create(UserCreate(
                key=test_user_key,
                email=test_user_key,
                first_name="SDK",
                last_name="Test",
            ))
            print(f"✓ Created user: {new_user.key}")
            
            # Get
            fetched = permissio.api.users.get(test_user_key)
            print(f"✓ Fetched user: {fetched.key}")
            
            # Delete
            permissio.api.users.delete(test_user_key)
            print(f"✓ Deleted user: {test_user_key}")
            
        except PermissioApiError as e:
            print(f"✗ Error: {e.message} (status: {e.status_code})")
            # Try to clean up
            try:
                permissio.api.users.delete(test_user_key)
            except:
                pass
        
        # =====================================================================
        # Test 6: Permission Check
        # =====================================================================
        print("\n--- Test 6: Permission Check ---")
        try:
            # Get a user and resource to test with
            users = permissio.api.users.list(per_page=1)
            resources = permissio.api.resources.list(per_page=1)
            
            if users.data and resources.data:
                user_key = users.data[0].key
                resource_key = resources.data[0].key
                
                allowed = permissio.check(user_key, "read", resource_key)
                print(f"✓ Check result: {user_key} can read {resource_key}: {allowed}")
            else:
                print("⚠ No users or resources found for permission check test")
                
        except PermissioApiError as e:
            print(f"✗ Error: {e.message} (status: {e.status_code})")
        
        print("\n" + "=" * 60)
        print("Tests completed!")
        print("=" * 60)
        
    finally:
        permissio.close()


if __name__ == "__main__":
    main()
