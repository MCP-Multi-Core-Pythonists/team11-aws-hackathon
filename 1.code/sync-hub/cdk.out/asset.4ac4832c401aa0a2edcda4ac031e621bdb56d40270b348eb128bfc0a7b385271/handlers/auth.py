import json
from typing import Dict, Any

def extract_claims(event: Dict[str, Any]) -> Dict[str, str]:
    """Extract JWT claims from API Gateway event"""
    try:
        authorizer = event.get("requestContext", {}).get("authorizer", {})
        jwt_claims = authorizer.get("jwt", {}).get("claims", {})
        
        return {
            "tenant_id": jwt_claims.get("tenant_id", "default"),
            "is_admin": jwt_claims.get("is_admin", "false"),
            "email": jwt_claims.get("email", ""),
            "sub": jwt_claims.get("sub", "")
        }
    except Exception as e:
        print(f"Error extracting claims: {e}")
        return {
            "tenant_id": "default",
            "is_admin": "false",
            "email": "",
            "sub": ""
        }
