import json
import os
from typing import Dict, Any
from handlers.auth import extract_claims
from handlers.settings import SettingsHandler
from handlers.groups import GroupsHandler
from handlers.admin import AdminHandler

# Initialize handlers
settings_handler = SettingsHandler()
groups_handler = GroupsHandler()
admin_handler = AdminHandler()

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    try:
        method = event.get("requestContext", {}).get("http", {}).get("method")
        path = event.get("requestContext", {}).get("http", {}).get("path")
        
        print(f"Processing {method} {path}")
        
        # Health check
        if path == "/_health":
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"ok": True, "message": "Sync Hub API is running!"})
            }
        
        # Extract claims from JWT
        claims = extract_claims(event)
        tenant_id = claims.get("tenant_id", "default")
        is_admin = claims.get("is_admin", "false") == "true"
        
        # Route to appropriate handler
        if path.startswith("/settings"):
            return settings_handler.handle(event, tenant_id)
        elif path.startswith("/groups"):
            return groups_handler.handle(event, tenant_id)
        elif path.startswith("/admin/"):
            if not is_admin:
                return {
                    "statusCode": 403,
                    "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"error": "Admin access required"})
                }
            return admin_handler.handle(event, tenant_id)
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Not found"})
            }
            
    except Exception as e:
        print(f"Unhandled error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Internal server error"})
        }
