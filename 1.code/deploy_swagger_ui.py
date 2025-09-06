#!/usr/bin/env python3
import boto3
import json
import yaml
import os
import time
import requests

# Configuration
REGION = "us-east-1"
BUCKET_NAME = "sync-hub-web-1757132517"
DISTRIBUTION_ID = "EPUT16LI6OAAI"
CLOUDFRONT_DOMAIN = "d1iz4bwpzq14da.cloudfront.net"
API_BASE_URL = "https://l7ycatge3j.execute-api.us-east-1.amazonaws.com"

def main():
    print("📚 Deploying Swagger UI for Sync Hub API...")
    
    # 1. Create OpenAPI 3.0.3 specification
    print("\n1️⃣ Creating OpenAPI 3.0.3 specification...")
    
    openapi_spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Sync Hub API",
            "description": "Multi-tenant SaaS for VS Code Extension + Web Console settings synchronization",
            "version": "1.0.0",
            "contact": {
                "name": "Sync Hub Support",
                "email": "support@synchub.dev"
            }
        },
        "servers": [
            {
                "url": API_BASE_URL,
                "description": "Production API"
            }
        ],
        "security": [
            {"bearerAuth": []}
        ],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT token from Cognito Hosted UI"
                }
            },
            "schemas": {
                "Error": {
                    "type": "object",
                    "required": ["error"],
                    "properties": {
                        "error": {"type": "string", "description": "Error message"},
                        "detail": {"type": "string", "description": "Additional error details"},
                        "request_id": {"type": "string", "description": "Request ID for tracking"}
                    }
                },
                "Setting": {
                    "type": "object",
                    "required": ["id", "name", "content", "visibility", "created_at", "updated_at"],
                    "properties": {
                        "id": {"type": "string", "example": "settings_123456"},
                        "name": {"type": "string", "example": "vscode-settings"},
                        "content": {"type": "object", "example": {"editor.fontSize": 14}},
                        "visibility": {"type": "string", "enum": ["private", "public", "group"], "example": "private"},
                        "group_id": {"type": "string", "nullable": True, "example": "group_789"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"},
                        "version": {"type": "integer", "example": 1}
                    }
                },
                "Group": {
                    "type": "object",
                    "required": ["id", "name", "created_at"],
                    "properties": {
                        "id": {"type": "string", "example": "group_123"},
                        "name": {"type": "string", "example": "Development Team"},
                        "description": {"type": "string", "example": "Settings for the dev team"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "member_count": {"type": "integer", "example": 5}
                    }
                },
                "GroupMember": {
                    "type": "object",
                    "required": ["user_id", "email", "role", "joined_at"],
                    "properties": {
                        "user_id": {"type": "string", "example": "user_456"},
                        "email": {"type": "string", "format": "email", "example": "user@example.com"},
                        "role": {"type": "string", "enum": ["member", "admin"], "example": "member"},
                        "joined_at": {"type": "string", "format": "date-time"}
                    }
                },
                "CreateSettingRequest": {
                    "type": "object",
                    "required": ["name", "content"],
                    "properties": {
                        "name": {"type": "string", "example": "my-vscode-config"},
                        "content": {"type": "object", "example": {"editor.fontSize": 16}},
                        "visibility": {"type": "string", "enum": ["private", "public", "group"], "default": "private"},
                        "group_id": {"type": "string", "description": "Required if visibility is 'group'"}
                    }
                },
                "CreateGroupRequest": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string", "example": "My Team"},
                        "description": {"type": "string", "example": "Shared settings for my team"}
                    }
                }
            }
        },
        "paths": {
            "/_health": {
                "get": {
                    "summary": "Health check",
                    "description": "Check API health status",
                    "security": [],
                    "responses": {
                        "200": {
                            "description": "API is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "ok": {"type": "boolean", "example": True},
                                            "message": {"type": "string", "example": "Sync Hub API is running!"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/settings": {
                "post": {
                    "summary": "Create a new setting",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CreateSettingRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Setting created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Setting"}
                                }
                            }
                        },
                        "400": {"description": "Invalid request", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                        "401": {"description": "Unauthorized", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                },
                "get": {
                    "summary": "List user's settings",
                    "parameters": [
                        {"name": "visibility", "in": "query", "schema": {"type": "string", "enum": ["private", "public", "group"]}},
                        {"name": "group_id", "in": "query", "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "200": {
                            "description": "Settings retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "settings": {"type": "array", "items": {"$ref": "#/components/schemas/Setting"}}
                                        }
                                    }
                                }
                            }
                        },
                        "401": {"description": "Unauthorized", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/settings/{id}": {
                "get": {
                    "summary": "Get a specific setting",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {
                        "200": {"description": "Setting retrieved", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Setting"}}}},
                        "404": {"description": "Setting not found", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                },
                "put": {
                    "summary": "Update a setting",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreateSettingRequest"}}}
                    },
                    "responses": {
                        "200": {"description": "Setting updated", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Setting"}}}},
                        "404": {"description": "Setting not found", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                },
                "delete": {
                    "summary": "Delete a setting",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {
                        "204": {"description": "Setting deleted successfully"},
                        "404": {"description": "Setting not found", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            },
            "/settings/{id}/history": {
                "get": {
                    "summary": "Get setting history",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {
                        "200": {
                            "description": "History retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "history": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "version": {"type": "integer"},
                                                        "content": {"type": "object"},
                                                        "updated_at": {"type": "string", "format": "date-time"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/settings/{id}/rollback": {
                "post": {
                    "summary": "Rollback setting to previous version",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["version"],
                                    "properties": {"version": {"type": "integer", "example": 2}}
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Setting rolled back", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Setting"}}}}
                    }
                }
            },
            "/settings/public": {
                "get": {
                    "summary": "List public settings",
                    "security": [],
                    "responses": {
                        "200": {
                            "description": "Public settings retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "settings": {"type": "array", "items": {"$ref": "#/components/schemas/Setting"}}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/settings/{id}/visibility": {
                "patch": {
                    "summary": "Update setting visibility",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["visibility"],
                                    "properties": {
                                        "visibility": {"type": "string", "enum": ["private", "public", "group"]},
                                        "group_id": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Visibility updated", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Setting"}}}}
                    }
                }
            },
            "/groups": {
                "post": {
                    "summary": "Create a new group",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreateGroupRequest"}}}
                    },
                    "responses": {
                        "201": {"description": "Group created", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Group"}}}}
                    }
                },
                "get": {
                    "summary": "List user's groups",
                    "responses": {
                        "200": {
                            "description": "Groups retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "groups": {"type": "array", "items": {"$ref": "#/components/schemas/Group"}}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/groups/{group_id}": {
                "get": {
                    "summary": "Get a specific group",
                    "parameters": [{"name": "group_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {
                        "200": {"description": "Group retrieved", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Group"}}}}
                    }
                },
                "patch": {
                    "summary": "Update a group",
                    "parameters": [{"name": "group_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "description": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Group updated", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Group"}}}}
                    }
                },
                "delete": {
                    "summary": "Delete a group",
                    "parameters": [{"name": "group_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {
                        "204": {"description": "Group deleted successfully"}
                    }
                }
            },
            "/groups/{group_id}/members": {
                "get": {
                    "summary": "List group members",
                    "parameters": [{"name": "group_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {
                        "200": {
                            "description": "Members retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "members": {"type": "array", "items": {"$ref": "#/components/schemas/GroupMember"}}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/groups/{group_id}/members/{user_id}": {
                "patch": {
                    "summary": "Update group member",
                    "parameters": [
                        {"name": "group_id", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "user_id", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["role"],
                                    "properties": {"role": {"type": "string", "enum": ["member", "admin"]}}
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Member updated", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/GroupMember"}}}}
                    }
                },
                "delete": {
                    "summary": "Remove group member",
                    "parameters": [
                        {"name": "group_id", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "user_id", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "204": {"description": "Member removed successfully"}
                    }
                }
            },
            "/admin/groups/{group_id}/members": {
                "post": {
                    "summary": "Add member to group (Admin only)",
                    "description": "Add a new member to a group (requires is_admin=true claim)",
                    "parameters": [{"name": "group_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["email"],
                                    "properties": {
                                        "email": {"type": "string", "format": "email", "example": "newuser@example.com"},
                                        "role": {"type": "string", "enum": ["member", "admin"], "default": "member"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Member added", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/GroupMember"}}}},
                        "403": {"description": "Admin privileges required", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}}
                    }
                }
            }
        }
    }
    
    print("✅ Created OpenAPI 3.0.3 specification")
    
    # 2. Create Swagger UI index.html
    print("\n2️⃣ Creating Swagger UI...")
    
    swagger_html = '''<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Sync Hub API Docs</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet"
      href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.ui = SwaggerUIBundle({
        url: "/docs/openapi.json",
        dom_id: "#swagger-ui",
        deepLinking: true,
        presets: [SwaggerUIBundle.presets.apis],
        layout: "BaseLayout"
      });
    </script>
  </body>
</html>'''
    
    # 3. Save files locally
    print("\n3️⃣ Saving documentation files...")
    
    os.makedirs('docs', exist_ok=True)
    
    # Save OpenAPI files
    with open('docs/openapi.json', 'w') as f:
        json.dump(openapi_spec, f, indent=2)
    
    with open('docs/openapi.yaml', 'w') as f:
        yaml.dump(openapi_spec, f, default_flow_style=False, sort_keys=False)
    
    # Save Swagger UI
    with open('docs/index.html', 'w') as f:
        f.write(swagger_html)
    
    print("✅ Saved documentation files locally")
    
    # 4. Upload to S3
    print("\n4️⃣ Uploading to S3...")
    
    s3 = boto3.client('s3', region_name=REGION)
    
    files_to_upload = [
        ('docs/index.html', 'text/html'),
        ('docs/openapi.json', 'application/json'),
        ('docs/openapi.yaml', 'application/x-yaml')
    ]
    
    for file_path, content_type in files_to_upload:
        s3.upload_file(
            file_path, BUCKET_NAME, file_path,
            ExtraArgs={
                'ContentType': content_type,
                'CacheControl': 'max-age=300'
            }
        )
    
    print(f"✅ Uploaded {len(files_to_upload)} files to S3")
    
    # 5. Create CloudFront invalidation
    print("\n5️⃣ Creating CloudFront invalidation...")
    
    cloudfront = boto3.client('cloudfront', region_name=REGION)
    
    invalidation = cloudfront.create_invalidation(
        DistributionId=DISTRIBUTION_ID,
        InvalidationBatch={
            'Paths': {
                'Quantity': 1,
                'Items': ['/*']
            },
            'CallerReference': str(int(time.time()))
        }
    )
    
    invalidation_id = invalidation['Invalidation']['Id']
    print(f"✅ Created invalidation: {invalidation_id}")
    
    # 6. Wait and run smoke tests
    print("\n6️⃣ Running smoke tests...")
    print("⏳ Waiting 30 seconds for invalidation...")
    time.sleep(30)
    
    test_results = {}
    
    # Test OpenAPI JSON
    try:
        response = requests.get(f"https://{CLOUDFRONT_DOMAIN}/docs/openapi.json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('openapi', '').startswith('3.0'):
                test_results['openapi_json'] = "✅ HTTP 200, contains openapi: 3.0.3"
            else:
                test_results['openapi_json'] = "⚠️ HTTP 200, but invalid OpenAPI format"
        else:
            test_results['openapi_json'] = f"⚠️ HTTP {response.status_code}"
    except Exception as e:
        test_results['openapi_json'] = f"❌ Error: {e}"
    
    # Test Swagger UI
    try:
        response = requests.get(f"https://{CLOUDFRONT_DOMAIN}/docs/", timeout=15)
        if response.status_code == 200 and 'swagger-ui' in response.text.lower():
            test_results['swagger_ui'] = "✅ HTTP 200, Swagger UI renders"
        else:
            test_results['swagger_ui'] = f"⚠️ HTTP {response.status_code}"
    except Exception as e:
        test_results['swagger_ui'] = f"❌ Error: {e}"
    
    # Test API health
    try:
        response = requests.get(f"{API_BASE_URL}/_health", timeout=10)
        test_results['api_health'] = f"✅ HTTP {response.status_code}" if response.status_code == 200 else f"⚠️ HTTP {response.status_code}"
    except Exception as e:
        test_results['api_health'] = f"❌ Error: {e}"
    
    # List S3 objects
    try:
        s3_objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='docs/')
        if 'Contents' in s3_objects:
            s3_files = [obj['Key'] for obj in s3_objects['Contents']]
        else:
            s3_files = []
    except Exception as e:
        s3_files = [f"Error: {e}"]
    
    # Final output
    print("\n" + "="*60)
    print("📚 SWAGGER UI DEPLOYMENT RESULTS")
    print("="*60)
    
    print(f"✅ CloudFront Swagger UI: https://{CLOUDFRONT_DOMAIN}/docs/")
    print(f"✅ OpenAPI JSON: https://{CLOUDFRONT_DOMAIN}/docs/openapi.json")
    print(f"✅ OpenAPI YAML: https://{CLOUDFRONT_DOMAIN}/docs/openapi.yaml")
    print(f"⚠️ API route: GET {API_BASE_URL}/docs/openapi.json (requires Lambda setup)")
    print(f"✅ CloudFront invalidation ID: {invalidation_id}")
    
    print(f"\n📁 S3 object listing under /docs:")
    for file in s3_files:
        print(f"   - {file}")
    
    print(f"\n🧪 Smoke test results:")
    for test_name, result in test_results.items():
        print(f"   - {test_name}: {result}")
    
    print(f"\n📊 API Documentation Summary:")
    paths_count = len(openapi_spec['paths'])
    print(f"   - OpenAPI version: 3.0.3")
    print(f"   - Total endpoints: {paths_count}")
    print(f"   - Security: JWT Bearer authentication")
    print(f"   - Public endpoints: /_health, /settings/public")
    print(f"   - Admin endpoints: /admin/groups/{{group_id}}/members")
    
    print(f"\n🔗 Quick access:")
    print(f"   - Interactive docs: https://{CLOUDFRONT_DOMAIN}/docs/")
    print(f"   - Raw spec: https://{CLOUDFRONT_DOMAIN}/docs/openapi.json")

if __name__ == "__main__":
    main()
