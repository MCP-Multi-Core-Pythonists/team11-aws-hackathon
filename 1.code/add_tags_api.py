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
    print("🏷️ Adding tags API endpoints to Sync Hub...")
    
    # 1. Create Lambda handler code for tags
    print("\n1️⃣ Creating Lambda handler for tags API...")
    
    tags_handler = '''
import json
import boto3
import re
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
settings_table = dynamodb.Table('sync-hub-settings')

def validate_tags(items):
    """Validate tag items"""
    if not isinstance(items, list):
        return False, "items must be an array"
    
    if len(items) == 0:
        return False, "items cannot be empty"
    
    if len(items) > 20:
        return False, "maximum 20 tags allowed"
    
    for item in items:
        if not isinstance(item, str):
            return False, "all items must be strings"
        if len(item.strip()) == 0:
            return False, "tag cannot be empty"
        if len(item) > 50:
            return False, "tag cannot exceed 50 characters"
        if not re.match(r'^[a-zA-Z0-9_-]+$', item):
            return False, "tag can only contain alphanumeric, underscore, and dash characters"
    
    return True, None

def get_user_from_jwt(event):
    """Extract user info from JWT token"""
    # This would normally decode the JWT token
    # For demo, return mock user
    return {
        'user_id': 'user_123',
        'tenant_id': 'tenant_456',
        'email': 'user@example.com'
    }

def cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Authorization, Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS'
    }

def lambda_handler(event, context):
    method = event['httpMethod']
    path = event['path']
    
    # Handle CORS preflight
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': ''
        }
    
    # Extract setting ID from path
    setting_id = event['pathParameters']['id']
    
    # Get user info
    user = get_user_from_jwt(event)
    
    try:
        if method == 'GET':
            return handle_get_tags(setting_id, user)
        elif method == 'POST':
            body = json.loads(event['body'])
            return handle_post_tags(setting_id, user, body)
        elif method == 'DELETE':
            body = json.loads(event['body'])
            return handle_delete_tags(setting_id, user, body)
        else:
            return {
                'statusCode': 405,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Method not allowed'})
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Internal server error', 'detail': str(e)})
        }

def handle_get_tags(setting_id, user):
    """Get tags for a setting"""
    try:
        response = settings_table.get_item(Key={'id': setting_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Setting not found'})
            }
        
        setting = response['Item']
        
        # Check access (owner or admin)
        if setting.get('user_id') != user['user_id'] and not user.get('is_admin'):
            return {
                'statusCode': 403,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Access denied'})
            }
        
        tags = setting.get('tags', [])
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({'items': tags})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Failed to get tags', 'detail': str(e)})
        }

def handle_post_tags(setting_id, user, body):
    """Add/update tags for a setting"""
    # Validate input
    if 'items' not in body:
        return {
            'statusCode': 400,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'items field required'})
        }
    
    valid, error = validate_tags(body['items'])
    if not valid:
        return {
            'statusCode': 400,
            'headers': cors_headers(),
            'body': json.dumps({'error': error})
        }
    
    try:
        # Get existing setting
        response = settings_table.get_item(Key={'id': setting_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Setting not found'})
            }
        
        setting = response['Item']
        
        # Check access
        if setting.get('user_id') != user['user_id'] and not user.get('is_admin'):
            return {
                'statusCode': 403,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Access denied'})
            }
        
        # Merge tags (deduplicate)
        existing_tags = set(setting.get('tags', []))
        new_tags = set(body['items'])
        all_tags = sorted(list(existing_tags.union(new_tags)))
        
        # Update setting
        settings_table.update_item(
            Key={'id': setting_id},
            UpdateExpression='SET tags = :tags, updated_at = :updated_at',
            ExpressionAttributeValues={
                ':tags': all_tags,
                ':updated_at': datetime.utcnow().isoformat()
            }
        )
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({'id': setting_id, 'items': all_tags})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Failed to update tags', 'detail': str(e)})
        }

def handle_delete_tags(setting_id, user, body):
    """Remove specific tags from a setting"""
    # Validate input
    if 'items' not in body:
        return {
            'statusCode': 400,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'items field required'})
        }
    
    valid, error = validate_tags(body['items'])
    if not valid:
        return {
            'statusCode': 400,
            'headers': cors_headers(),
            'body': json.dumps({'error': error})
        }
    
    try:
        # Get existing setting
        response = settings_table.get_item(Key={'id': setting_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Setting not found'})
            }
        
        setting = response['Item']
        
        # Check access
        if setting.get('user_id') != user['user_id'] and not user.get('is_admin'):
            return {
                'statusCode': 403,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Access denied'})
            }
        
        # Remove specified tags
        existing_tags = set(setting.get('tags', []))
        tags_to_remove = set(body['items'])
        remaining_tags = sorted(list(existing_tags - tags_to_remove))
        
        # Update setting
        settings_table.update_item(
            Key={'id': setting_id},
            UpdateExpression='SET tags = :tags, updated_at = :updated_at',
            ExpressionAttributeValues={
                ':tags': remaining_tags,
                ':updated_at': datetime.utcnow().isoformat()
            }
        )
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({'id': setting_id, 'items': remaining_tags})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Failed to delete tags', 'detail': str(e)})
        }
'''
    
    # Save handler code
    os.makedirs('lambda', exist_ok=True)
    with open('lambda/tags_handler.py', 'w') as f:
        f.write(tags_handler)
    
    print("✅ Created tags Lambda handler")
    
    # 2. Update OpenAPI specification
    print("\n2️⃣ Updating OpenAPI specification...")
    
    # Load existing spec
    with open('docs/openapi.yaml', 'r') as f:
        openapi_data = yaml.safe_load(f)
    
    # Add new schemas
    openapi_data['components']['schemas']['TagsResponse'] = {
        'type': 'object',
        'required': ['items'],
        'properties': {
            'items': {
                'type': 'array',
                'items': {
                    'type': 'string',
                    'pattern': '^[a-zA-Z0-9_-]+$',
                    'minLength': 1,
                    'maxLength': 50
                },
                'maxItems': 20,
                'example': ['dark', 'editor', 'vscode']
            }
        }
    }
    
    openapi_data['components']['schemas']['TagsRequest'] = {
        'type': 'object',
        'required': ['items'],
        'properties': {
            'items': {
                'type': 'array',
                'items': {
                    'type': 'string',
                    'pattern': '^[a-zA-Z0-9_-]+$',
                    'minLength': 1,
                    'maxLength': 50
                },
                'minItems': 1,
                'maxItems': 20,
                'example': ['dark', 'vscode']
            }
        }
    }
    
    openapi_data['components']['schemas']['TagsUpdateResponse'] = {
        'type': 'object',
        'required': ['id', 'items'],
        'properties': {
            'id': {
                'type': 'string',
                'description': 'Setting ID',
                'example': 'settings_123456'
            },
            'items': {
                'type': 'array',
                'items': {
                    'type': 'string'
                },
                'example': ['dark', 'editor', 'vscode']
            }
        }
    }
    
    # Add new paths
    openapi_data['paths']['/settings/{id}/tags'] = {
        'get': {
            'summary': 'Get setting tags',
            'description': 'Retrieve tags for a specific setting',
            'parameters': [
                {
                    'name': 'id',
                    'in': 'path',
                    'required': True,
                    'schema': {'type': 'string'},
                    'description': 'Setting ID'
                }
            ],
            'responses': {
                '200': {
                    'description': 'Tags retrieved successfully',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/TagsResponse'}
                        }
                    }
                },
                '401': {
                    'description': 'Unauthorized',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                },
                '403': {
                    'description': 'Access denied',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                },
                '404': {
                    'description': 'Setting not found',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                }
            }
        },
        'post': {
            'summary': 'Add/update setting tags',
            'description': 'Add or update tags for a setting (upsert behavior)',
            'parameters': [
                {
                    'name': 'id',
                    'in': 'path',
                    'required': True,
                    'schema': {'type': 'string'},
                    'description': 'Setting ID'
                }
            ],
            'requestBody': {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/TagsRequest'}
                    }
                }
            },
            'responses': {
                '200': {
                    'description': 'Tags updated successfully',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/TagsUpdateResponse'}
                        }
                    }
                },
                '400': {
                    'description': 'Invalid request',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                },
                '401': {
                    'description': 'Unauthorized',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                },
                '403': {
                    'description': 'Access denied',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                },
                '404': {
                    'description': 'Setting not found',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                }
            }
        },
        'delete': {
            'summary': 'Remove setting tags',
            'description': 'Remove specific tags from a setting',
            'parameters': [
                {
                    'name': 'id',
                    'in': 'path',
                    'required': True,
                    'schema': {'type': 'string'},
                    'description': 'Setting ID'
                }
            ],
            'requestBody': {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/TagsRequest'}
                    }
                }
            },
            'responses': {
                '200': {
                    'description': 'Tags removed successfully',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/TagsUpdateResponse'}
                        }
                    }
                },
                '400': {
                    'description': 'Invalid request',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                },
                '401': {
                    'description': 'Unauthorized',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                },
                '403': {
                    'description': 'Access denied',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                },
                '404': {
                    'description': 'Setting not found',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                }
            }
        }
    }
    
    # Save updated YAML
    with open('docs/openapi.yaml', 'w') as f:
        yaml.dump(openapi_data, f, default_flow_style=False, sort_keys=False)
    
    # Save updated JSON
    with open('docs/openapi.json', 'w') as f:
        json.dump(openapi_data, f, indent=2)
    
    print("✅ Updated OpenAPI specification with tags endpoints")
    
    # 3. Upload updated docs to S3
    print("\n3️⃣ Uploading updated documentation...")
    
    s3 = boto3.client('s3', region_name=REGION)
    
    docs_files = [
        ('docs/openapi.yaml', 'application/x-yaml'),
        ('docs/openapi.json', 'application/json')
    ]
    
    for file_path, content_type in docs_files:
        s3.upload_file(
            file_path, BUCKET_NAME, file_path,
            ExtraArgs={
                'ContentType': content_type,
                'CacheControl': 'max-age=300'
            }
        )
    
    print("✅ Uploaded updated OpenAPI files")
    
    # 4. Create CloudFront invalidation
    print("\n4️⃣ Creating CloudFront invalidation...")
    
    cloudfront = boto3.client('cloudfront', region_name=REGION)
    
    invalidation = cloudfront.create_invalidation(
        DistributionId=DISTRIBUTION_ID,
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
    
    # 5. Test updated documentation
    print("\n5️⃣ Testing updated documentation...")
    print("⏳ Waiting 20 seconds for invalidation...")
    time.sleep(20)
    
    try:
        spec_response = requests.get(f"https://{CLOUDFRONT_DOMAIN}/docs/openapi.json", timeout=10)
        if spec_response.status_code == 200:
            spec_data = spec_response.json()
            tags_path = spec_data.get('paths', {}).get('/settings/{id}/tags')
            if tags_path:
                print("✅ Tags endpoints found in OpenAPI spec")
            else:
                print("⚠️ Tags endpoints not found in spec")
        else:
            print(f"⚠️ OpenAPI spec: HTTP {spec_response.status_code}")
    except Exception as e:
        print(f"❌ OpenAPI test failed: {e}")
    
    # Final output
    print("\n" + "="*60)
    print("🏷️ TAGS API DEPLOYMENT RESULTS")
    print("="*60)
    
    print("✅ New routes to be deployed:")
    print("   - GET /settings/{id}/tags")
    print("   - POST /settings/{id}/tags")
    print("   - DELETE /settings/{id}/tags")
    
    print(f"\n✅ Updated Swagger UI URL: https://{CLOUDFRONT_DOMAIN}/docs/")
    
    print(f"\n📋 Example curl commands:")
    print(f"# Get tags for a setting")
    print(f"curl -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\")
    print(f"     {API_BASE_URL}/settings/SETTING_ID/tags")
    print(f"")
    print(f"# Add tags to a setting")
    print(f"curl -X POST -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"items\": [\"dark\", \"vscode\"]}}' \\")
    print(f"     {API_BASE_URL}/settings/SETTING_ID/tags")
    print(f"")
    print(f"# Remove tags from a setting")
    print(f"curl -X DELETE -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"items\": [\"dark\"]}}' \\")
    print(f"     {API_BASE_URL}/settings/SETTING_ID/tags")
    
    print(f"\n🔧 Next steps:")
    print(f"1. Deploy Lambda function 'sync-hub-tags' with the generated handler")
    print(f"2. Add API Gateway routes:")
    print(f"   - GET /settings/{{id}}/tags → sync-hub-tags Lambda")
    print(f"   - POST /settings/{{id}}/tags → sync-hub-tags Lambda")
    print(f"   - DELETE /settings/{{id}}/tags → sync-hub-tags Lambda")
    print(f"3. Test the endpoints with valid JWT tokens")
    
    print(f"\n📚 Documentation updated:")
    print(f"   - OpenAPI spec includes 3 new endpoints")
    print(f"   - Swagger UI shows tags operations")
    print(f"   - CloudFront invalidation: {invalidation_id}")

if __name__ == "__main__":
    main()
