"""
Flask integration example for the Permissio.io Python SDK.

This example demonstrates:
- Integrating Permissio.io with Flask
- Creating permission decorators
- Middleware for permission checking
- Async support with Flask-Async
"""

from functools import wraps
from typing import Optional, Callable, Any

from flask import Flask, g, request, jsonify, abort

from permissio import Permissio
from permissio.errors import PermissioApiError, PermissioNotFoundError


# ============================================================================
# Flask Application Setup
# ============================================================================

app = Flask(__name__)

# Initialize Permissio.io client
# In production, load these from environment variables
permissio = Permissio(
    token="permis_key_your_api_key_here",
    project_id="my-project",
    environment_id="production",
)


# ============================================================================
# Authentication Middleware (Example)
# ============================================================================

@app.before_request
def authenticate():
    """
    Example authentication middleware.
    Replace with your actual authentication logic.
    """
    # Get auth token from header
    auth_header = request.headers.get("Authorization", "")
    
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # In a real app, validate the token and get user info
        # For this example, we'll use a simple mock
        g.user_id = token  # Use token as user ID for demo
        g.user = {
            "id": token,
            "email": f"{token}@example.com",
            "tenant": request.headers.get("X-Tenant-ID", "default"),
        }
    else:
        g.user_id = None
        g.user = None


# ============================================================================
# Permission Decorators
# ============================================================================

def require_permission(action: str, resource: str, get_resource_key: Optional[Callable] = None):
    """
    Decorator to require a specific permission for a route.
    
    Args:
        action: The action to check (e.g., "read", "write", "delete")
        resource: The resource type (e.g., "document", "project")
        get_resource_key: Optional callable to extract resource key from request
    
    Example:
        @app.route("/documents/<doc_id>")
        @require_permission("read", "document", lambda: request.view_args.get("doc_id"))
        def get_document(doc_id):
            return {"id": doc_id}
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.user_id:
                abort(401, description="Authentication required")
            
            # Build resource for check
            resource_data = {"type": resource}
            
            # Add resource key if provided
            if get_resource_key:
                resource_key = get_resource_key()
                if resource_key:
                    resource_data["key"] = resource_key
            
            # Add tenant if available
            if g.user and g.user.get("tenant"):
                resource_data["tenant"] = g.user["tenant"]
            
            # Check permission
            allowed = permissio.check(g.user_id, action, resource_data)
            
            if not allowed:
                abort(403, description=f"Permission denied: {action} on {resource}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_any_permission(*permissions):
    """
    Decorator to require any of the specified permissions.
    
    Args:
        permissions: Tuples of (action, resource)
    
    Example:
        @app.route("/documents")
        @require_any_permission(("read", "document"), ("admin", "document"))
        def list_documents():
            return {"documents": [...]}
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.user_id:
                abort(401, description="Authentication required")
            
            # Check each permission
            for action, resource in permissions:
                resource_data = {"type": resource}
                if g.user and g.user.get("tenant"):
                    resource_data["tenant"] = g.user["tenant"]
                
                if permissio.check(g.user_id, action, resource_data):
                    return f(*args, **kwargs)
            
            abort(403, description="Permission denied")
        return decorated_function
    return decorator


def require_all_permissions(*permissions):
    """
    Decorator to require all of the specified permissions.
    
    Args:
        permissions: Tuples of (action, resource)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.user_id:
                abort(401, description="Authentication required")
            
            # Build bulk check
            checks = []
            for action, resource in permissions:
                resource_data = {"type": resource}
                if g.user and g.user.get("tenant"):
                    resource_data["tenant"] = g.user["tenant"]
                
                checks.append({
                    "user": g.user_id,
                    "action": action,
                    "resource": resource_data,
                })
            
            # Bulk check
            results = permissio.bulk_check(checks)
            
            if not results.all_allowed():
                abort(403, description="Permission denied")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================================
# Permission Helper Functions
# ============================================================================

def can_user(action: str, resource: str, resource_key: Optional[str] = None) -> bool:
    """
    Check if the current user can perform an action.
    Use this for conditional logic in templates or responses.
    """
    if not g.user_id:
        return False
    
    resource_data = {"type": resource}
    if resource_key:
        resource_data["key"] = resource_key
    if g.user and g.user.get("tenant"):
        resource_data["tenant"] = g.user["tenant"]
    
    return permissio.check(g.user_id, action, resource_data)


# ============================================================================
# API Routes
# ============================================================================

@app.route("/")
def index():
    """Public route - no permission required."""
    return jsonify({
        "message": "Welcome to the Permissio.io Flask example",
        "endpoints": [
            "GET /documents",
            "GET /documents/<id>",
            "POST /documents",
            "PUT /documents/<id>",
            "DELETE /documents/<id>",
            "GET /admin/users",
        ]
    })


@app.route("/documents")
@require_permission("read", "document")
def list_documents():
    """List documents - requires read permission."""
    # In a real app, fetch from database
    documents = [
        {"id": "doc-1", "title": "Document 1", "can_edit": can_user("write", "document", "doc-1")},
        {"id": "doc-2", "title": "Document 2", "can_edit": can_user("write", "document", "doc-2")},
        {"id": "doc-3", "title": "Document 3", "can_edit": can_user("write", "document", "doc-3")},
    ]
    return jsonify({"documents": documents})


@app.route("/documents/<doc_id>")
@require_permission("read", "document", lambda: request.view_args.get("doc_id"))
def get_document(doc_id):
    """Get a specific document - requires read permission on the document."""
    # In a real app, fetch from database
    document = {
        "id": doc_id,
        "title": f"Document {doc_id}",
        "content": "This is the document content...",
        "permissions": {
            "can_read": True,  # Already verified by decorator
            "can_write": can_user("write", "document", doc_id),
            "can_delete": can_user("delete", "document", doc_id),
        }
    }
    return jsonify(document)


@app.route("/documents", methods=["POST"])
@require_permission("create", "document")
def create_document():
    """Create a document - requires create permission."""
    data = request.get_json()
    
    # In a real app, save to database
    new_doc = {
        "id": "doc-new",
        "title": data.get("title", "Untitled"),
        "content": data.get("content", ""),
    }
    
    return jsonify(new_doc), 201


@app.route("/documents/<doc_id>", methods=["PUT"])
@require_permission("write", "document", lambda: request.view_args.get("doc_id"))
def update_document(doc_id):
    """Update a document - requires write permission on the document."""
    data = request.get_json()
    
    # In a real app, update in database
    updated_doc = {
        "id": doc_id,
        "title": data.get("title", f"Document {doc_id}"),
        "content": data.get("content", ""),
    }
    
    return jsonify(updated_doc)


@app.route("/documents/<doc_id>", methods=["DELETE"])
@require_permission("delete", "document", lambda: request.view_args.get("doc_id"))
def delete_document(doc_id):
    """Delete a document - requires delete permission on the document."""
    # In a real app, delete from database
    return jsonify({"message": f"Document {doc_id} deleted"}), 200


@app.route("/admin/users")
@require_all_permissions(("read", "user"), ("admin", "system"))
def admin_list_users():
    """Admin route - requires both read:user and admin:system permissions."""
    # In a real app, fetch from database
    users = [
        {"id": "user-1", "email": "user1@example.com"},
        {"id": "user-2", "email": "user2@example.com"},
    ]
    return jsonify({"users": users})


@app.route("/settings")
@require_any_permission(("read", "settings"), ("admin", "system"))
def get_settings():
    """Settings route - requires either read:settings or admin:system."""
    settings = {
        "theme": "dark",
        "language": "en",
        "notifications": True,
    }
    return jsonify({"settings": settings})


# ============================================================================
# User Sync Route
# ============================================================================

@app.route("/auth/sync", methods=["POST"])
def sync_user():
    """
    Sync user data with Permissio.io after authentication.
    Call this after your user logs in to ensure they exist in Permissio.io.
    """
    if not g.user_id:
        abort(401)
    
    data = request.get_json() or {}
    
    try:
        synced_user = permissio.sync_user({
            "key": g.user_id,
            "email": data.get("email", g.user.get("email")),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "attributes": data.get("attributes", {}),
        })
        
        return jsonify({
            "message": "User synced successfully",
            "user_key": synced_user.key,
        })
        
    except PermissioApiError as e:
        return jsonify({"error": e.message}), e.status_code


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "error": "Unauthorized",
        "message": str(error.description),
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "error": "Forbidden",
        "message": str(error.description),
    }), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": str(error.description),
    }), 404


# ============================================================================
# Cleanup
# ============================================================================

@app.teardown_appcontext
def cleanup(exception=None):
    """Cleanup on app context teardown."""
    # Note: In production, you might want to keep the client alive
    # and only close it when the app shuts down
    pass


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("Starting Flask app with Permissio.io integration...")
    print("Try these commands:")
    print("  curl http://localhost:5000/")
    print('  curl -H "Authorization: Bearer user123" http://localhost:5000/documents')
    print('  curl -H "Authorization: Bearer user123" http://localhost:5000/documents/doc-1')
    
    app.run(debug=True, port=5000)
