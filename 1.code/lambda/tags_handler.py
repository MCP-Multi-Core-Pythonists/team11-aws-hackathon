
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
