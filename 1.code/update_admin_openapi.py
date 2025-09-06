#!/usr/bin/env python3
"""
Update OpenAPI specification with admin endpoints and redeploy
"""
import yaml
import json
import boto3
import time

def update_openapi_with_admin():
    """Update OpenAPI spec with admin endpoints"""
    
    print("📚 Updating OpenAPI specification with admin endpoints...")
    
    # Load existing OpenAPI spec
    with open('docs/openapi.yaml', 'r') as f:
        openapi_data = yaml.safe_load(f)
    
    # Add new admin schemas
    admin_schemas = {
        "AdminUser": {
            "type": "object",
            "required": ["user_id", "email", "status", "created_at"],
            "properties": {
                "user_id": {"type": "string", "example": "user_123"},
                "email": {"type": "string", "format": "email", "example": "user@example.com"},
                "status": {"type": "string", "enum": ["CONFIRMED", "UNCONFIRMED", "ARCHIVED"], "example": "CONFIRMED"},
                "created_at": {"type": "string", "format": "date-time"},
                "enabled": {"type": "boolean", "example": True}
            }
        },
        "AdminUsersList": {
            "type": "object",
            "properties": {
                "users": {"type": "array", "items": {"$ref": "#/components/schemas/AdminUser"}},
                "next_cursor": {"type": "string", "nullable": True},
                "count": {"type": "integer", "example": 25}
            }
        },
        "UserLookupRequest": {
            "type": "object",
            "required": ["email"],
            "properties": {
                "email": {"type": "string", "format": "email", "example": "user@example.com"}
            }
        },
        "UserLookupResponse": {
            "type": "object",
            "properties": {
                "user": {"$ref": "#/components/schemas/AdminUser"}
            }
        },
        "UpdateMemberRequest": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "enum": ["member", "admin"], "example": "member"},
                "status": {"type": "string", "enum": ["active", "inactive"], "example": "active"}
            }
        },
        "AnalyticsResponse": {
            "type": "object",
            "properties": {
                "range": {"type": "string", "enum": ["1d", "7d", "30d"], "example": "7d"},
                "total_settings": {"type": "integer", "example": 150},
                "public_settings": {"type": "integer", "example": 25},
                "private_settings": {"type": "integer", "example": 125},
                "total_members": {"type": "integer", "example": 45},
                "active_members": {"type": "integer", "example": 40},
                "inactive_members": {"type": "integer", "example": 5},
                "generated_at": {"type": "string", "format": "date-time"}
            }
        },
        "TimeseriesDataPoint": {
            "type": "object",
            "properties": {
                "timestamp": {"type": "string", "format": "date-time"},
                "value": {"type": "integer", "example": 15},
                "metric": {"type": "string", "example": "settings"}
            }
        },
        "TimeseriesResponse": {
            "type": "object",
            "properties": {
                "metric": {"type": "string", "example": "settings"},
                "range": {"type": "string", "example": "7d"},
                "interval": {"type": "string", "example": "day"},
                "data": {"type": "array", "items": {"$ref": "#/components/schemas/TimeseriesDataPoint"}}
            }
        }
    }
    
    # Add schemas to OpenAPI spec
    openapi_data['components']['schemas'].update(admin_schemas)
    
    # Add new admin paths
    admin_paths = {
        "/admin/users": {
            "get": {
                "summary": "List users (Admin only)",
                "description": "List all users with pagination and search (requires is_admin=true)",
                "parameters": [
                    {"name": "query", "in": "query", "schema": {"type": "string"}, "description": "Search query for email"},
                    {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 20, "maximum": 60}, "description": "Number of users to return"},
                    {"name": "cursor", "in": "query", "schema": {"type": "string"}, "description": "Pagination cursor"}
                ],
                "responses": {
                    "200": {
                        "description": "Users retrieved successfully",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AdminUsersList"}}}
                    },
                    "403": {"description": "Admin privileges required", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                }
            }
        },
        "/admin/users/lookup": {
            "post": {
                "summary": "Lookup user by email (Admin only)",
                "description": "Find a user by email address (requires is_admin=true)",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserLookupRequest"}}}
                },
                "responses": {
                    "200": {
                        "description": "User found",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UserLookupResponse"}}}
                    },
                    "404": {"description": "User not found", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                    "403": {"description": "Admin privileges required", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                }
            }
        },
        "/admin/groups/{gid}/members/{uid}": {
            "patch": {
                "summary": "Update group member (Admin only)",
                "description": "Update a group member's role or status (requires is_admin=true)",
                "parameters": [
                    {"name": "gid", "in": "path", "required": True, "schema": {"type": "string"}, "description": "Group ID"},
                    {"name": "uid", "in": "path", "required": True, "schema": {"type": "string"}, "description": "User ID"}
                ],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UpdateMemberRequest"}}}
                },
                "responses": {
                    "200": {
                        "description": "Member updated successfully",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/GroupMember"}}}
                    },
                    "403": {"description": "Admin privileges required", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                    "404": {"description": "Member not found", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                }
            },
            "delete": {
                "summary": "Remove group member (Admin only)",
                "description": "Remove a member from a group (requires is_admin=true)",
                "parameters": [
                    {"name": "gid", "in": "path", "required": True, "schema": {"type": "string"}, "description": "Group ID"},
                    {"name": "uid", "in": "path", "required": True, "schema": {"type": "string"}, "description": "User ID"}
                ],
                "responses": {
                    "204": {"description": "Member removed successfully"},
                    "403": {"description": "Admin privileges required", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                    "404": {"description": "Member not found", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                }
            }
        },
        "/admin/analytics": {
            "get": {
                "summary": "Get analytics overview (Admin only)",
                "description": "Get analytics data for the tenant (requires is_admin=true)",
                "parameters": [
                    {"name": "range", "in": "query", "schema": {"type": "string", "enum": ["1d", "7d", "30d"], "default": "7d"}, "description": "Time range for analytics"}
                ],
                "responses": {
                    "200": {
                        "description": "Analytics data retrieved",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AnalyticsResponse"}}}
                    },
                    "403": {"description": "Admin privileges required", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                }
            }
        },
        "/admin/analytics/timeseries": {
            "get": {
                "summary": "Get analytics timeseries (Admin only)",
                "description": "Get timeseries analytics data (requires is_admin=true)",
                "parameters": [
                    {"name": "metric", "in": "query", "schema": {"type": "string", "default": "settings"}, "description": "Metric to retrieve"},
                    {"name": "range", "in": "query", "schema": {"type": "string", "enum": ["1d", "7d", "30d"], "default": "7d"}, "description": "Time range"},
                    {"name": "interval", "in": "query", "schema": {"type": "string", "enum": ["hour", "day"], "default": "day"}, "description": "Data interval"}
                ],
                "responses": {
                    "200": {
                        "description": "Timeseries data retrieved",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/TimeseriesResponse"}}}
                    },
                    "403": {"description": "Admin privileges required", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                }
            }
        }
    }
    
    # Add paths to OpenAPI spec
    openapi_data['paths'].update(admin_paths)
    
    # Save updated YAML
    with open('docs/openapi.yaml', 'w') as f:
        yaml.dump(openapi_data, f, default_flow_style=False, sort_keys=False)
    
    # Save updated JSON
    with open('docs/openapi.json', 'w') as f:
        json.dump(openapi_data, f, indent=2)
    
    print("✅ Updated OpenAPI specification with admin endpoints")
    
    # Upload to S3
    print("\n📤 Uploading updated OpenAPI files to S3...")
    
    s3 = boto3.client('s3', region_name='us-east-1')
    bucket_name = 'sync-hub-web-1757132517'
    
    files_to_upload = [
        ('docs/openapi.yaml', 'application/x-yaml'),
        ('docs/openapi.json', 'application/json')
    ]
    
    for file_path, content_type in files_to_upload:
        s3.upload_file(
            file_path, bucket_name, file_path,
            ExtraArgs={
                'ContentType': content_type,
                'CacheControl': 'max-age=300'
            }
        )
    
    print("✅ Uploaded updated OpenAPI files")
    
    # Create CloudFront invalidation
    print("\n🔄 Creating CloudFront invalidation...")
    
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    distribution_id = 'EPUT16LI6OAAI'
    
    invalidation = cloudfront.create_invalidation(
        DistributionId=distribution_id,
        InvalidationBatch={
            'Paths': {
                'Quantity': 1,
                'Items': ['/docs/*']
            },
            'CallerReference': str(int(time.time()))
        }
    )
    
    invalidation_id = invalidation['Invalidation']['Id']
    print(f"✅ Created invalidation: {invalidation_id}")
    
    print(f"\n📊 OpenAPI Summary:")
    total_paths = len(openapi_data['paths'])
    admin_paths_count = len([p for p in openapi_data['paths'].keys() if p.startswith('/admin')])
    print(f"  - Total endpoints: {total_paths}")
    print(f"  - Admin endpoints: {admin_paths_count}")
    print(f"  - New schemas: {len(admin_schemas)}")
    
    print(f"\n🔗 Updated documentation:")
    print(f"  - Swagger UI: https://d1iz4bwpzq14da.cloudfront.net/docs/")
    print(f"  - OpenAPI JSON: https://d1iz4bwpzq14da.cloudfront.net/docs/openapi.json")

if __name__ == "__main__":
    update_openapi_with_admin()
