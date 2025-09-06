import json
import boto3
import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
cognito = boto3.client('cognito-idp')

# Table references
group_members_table = dynamodb.Table('sync-hub-group-members')
settings_table = dynamodb.Table('sync-hub-settings')
audit_table = dynamodb.Table('sync-hub-audit')

USER_POOL_ID = 'us-east-1_ARkd0dYPj'

def get_user_from_jwt(event):
    """Extract user info from JWT token"""
    # Mock implementation - in production, decode JWT
    return {
        'user_id': 'user_123',
        'tenant_id': 'tenant_456',
        'email': 'admin@example.com',
        'is_admin': True
    }

def cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Authorization, Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS'
    }

def write_audit_event(user_id: str, tenant_id: str, action: str, resource: str, details: Dict):
    """Write audit event to audit table"""
    try:
        audit_table.put_item(
            Item={
                'id': f"AUDIT#{datetime.utcnow().isoformat()}#{user_id}",
                'tenant_id': tenant_id,
                'user_id': user_id,
                'action': action,
                'resource': resource,
                'details': details,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        print(f"Failed to write audit event: {e}")

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
    
    # Get user info and verify admin
    user = get_user_from_jwt(event)
    if not user.get('is_admin'):
        return {
            'statusCode': 403,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Admin privileges required'})
        }
    
    try:
        # Route to appropriate handler
        if path == '/admin/users' and method == 'GET':
            return handle_list_users(event, user)
        elif path == '/admin/users/lookup' and method == 'POST':
            return handle_lookup_user(event, user)
        elif path.startswith('/admin/groups/') and path.endswith('/members') and method == 'POST':
            return handle_add_member(event, user)
        elif '/admin/groups/' in path and '/members/' in path and method == 'PATCH':
            return handle_update_member(event, user)
        elif '/admin/groups/' in path and '/members/' in path and method == 'DELETE':
            return handle_remove_member(event, user)
        elif path == '/admin/analytics' and method == 'GET':
            return handle_analytics(event, user)
        elif path == '/admin/analytics/timeseries' and method == 'GET':
            return handle_analytics_timeseries(event, user)
        else:
            return {
                'statusCode': 404,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Endpoint not found'})
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Internal server error', 'detail': str(e)})
        }

def handle_list_users(event, user):
    """List users with pagination and search"""
    query_params = event.get('queryStringParameters') or {}
    query = query_params.get('query', '')
    limit = int(query_params.get('limit', '20'))
    cursor = query_params.get('cursor')
    
    try:
        # Query Cognito for users
        params = {
            'UserPoolId': USER_POOL_ID,
            'Limit': min(limit, 60)
        }
        
        if cursor:
            params['PaginationToken'] = cursor
        
        if query:
            params['Filter'] = f'email ^= "{query}"'
        
        response = cognito.list_users(**params)
        
        users = []
        for cognito_user in response.get('Users', []):
            user_attrs = {attr['Name']: attr['Value'] for attr in cognito_user.get('Attributes', [])}
            users.append({
                'user_id': cognito_user['Username'],
                'email': user_attrs.get('email', ''),
                'status': cognito_user['UserStatus'],
                'created_at': cognito_user['UserCreateDate'].isoformat(),
                'enabled': cognito_user['Enabled']
            })
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'users': users,
                'next_cursor': response.get('PaginationToken'),
                'count': len(users)
            }, default=str)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Failed to list users', 'detail': str(e)})
        }

def handle_lookup_user(event, user):
    """Lookup user by email"""
    try:
        body = json.loads(event['body'])
        email = body.get('email')
        
        if not email:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Email required'})
            }
        
        # Search Cognito by email
        response = cognito.list_users(
            UserPoolId=USER_POOL_ID,
            Filter=f'email = "{email}"',
            Limit=1
        )
        
        if not response.get('Users'):
            return {
                'statusCode': 404,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'User not found'})
            }
        
        cognito_user = response['Users'][0]
        user_attrs = {attr['Name']: attr['Value'] for attr in cognito_user.get('Attributes', [])}
        
        user_data = {
            'user_id': cognito_user['Username'],
            'email': user_attrs.get('email', ''),
            'status': cognito_user['UserStatus'],
            'created_at': cognito_user['UserCreateDate'].isoformat(),
            'enabled': cognito_user['Enabled']
        }
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({'user': user_data}, default=str)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Failed to lookup user', 'detail': str(e)})
        }

def handle_add_member(event, user):
    """Add member to group"""
    try:
        group_id = event['pathParameters']['gid']
        body = json.loads(event['body'])
        email = body.get('email')
        role = body.get('role', 'member')
        
        if not email or role not in ['member', 'admin']:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Valid email and role required'})
            }
        
        # Lookup user by email
        cognito_response = cognito.list_users(
            UserPoolId=USER_POOL_ID,
            Filter=f'email = "{email}"',
            Limit=1
        )
        
        if not cognito_response.get('Users'):
            return {
                'statusCode': 404,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'User not found'})
            }
        
        target_user_id = cognito_response['Users'][0]['Username']
        
        # Add to group_members table
        member_item = {
            'pk': f"TENANT#{user['tenant_id']}#GROUP#{group_id}",
            'sk': f"USER#{target_user_id}",
            'tenant_id': user['tenant_id'],
            'group_id': group_id,
            'user_id': target_user_id,
            'email': email,
            'role': role,
            'status': 'active',
            'joined_at': datetime.utcnow().isoformat(),
            'gsi1_pk': email,
            'gsi1_sk': f"TENANT#{user['tenant_id']}",
            'gsi2_pk': f"TENANT#{user['tenant_id']}",
            'gsi2_sk': f"GROUP#{group_id}"
        }
        
        group_members_table.put_item(Item=member_item)
        
        # Write audit event
        write_audit_event(
            user['user_id'], user['tenant_id'], 'ADD_MEMBER',
            f"GROUP#{group_id}", {'target_user': target_user_id, 'role': role}
        )
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'user_id': target_user_id,
                'email': email,
                'role': role,
                'status': 'active',
                'joined_at': member_item['joined_at']
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Failed to add member', 'detail': str(e)})
        }

def handle_update_member(event, user):
    """Update group member"""
    try:
        group_id = event['pathParameters']['gid']
        user_id = event['pathParameters']['uid']
        body = json.loads(event['body'])
        
        # Build update expression
        update_expr = "SET "
        expr_values = {}
        
        if 'role' in body and body['role'] in ['member', 'admin']:
            update_expr += "#role = :role, "
            expr_values[':role'] = body['role']
        
        if 'status' in body and body['status'] in ['active', 'inactive']:
            update_expr += "#status = :status, "
            expr_values[':status'] = body['status']
        
        if not expr_values:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'No valid fields to update'})
            }
        
        update_expr = update_expr.rstrip(', ')
        
        response = group_members_table.update_item(
            Key={
                'pk': f"TENANT#{user['tenant_id']}#GROUP#{group_id}",
                'sk': f"USER#{user_id}"
            },
            UpdateExpression=update_expr,
            ExpressionAttributeNames={'#role': 'role', '#status': 'status'},
            ExpressionAttributeValues=expr_values,
            ReturnValues='ALL_NEW'
        )
        
        # Write audit event
        write_audit_event(
            user['user_id'], user['tenant_id'], 'UPDATE_MEMBER',
            f"GROUP#{group_id}", {'target_user': user_id, 'changes': body}
        )
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps(response['Attributes'], default=str)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Failed to update member', 'detail': str(e)})
        }

def handle_remove_member(event, user):
    """Remove member from group"""
    try:
        group_id = event['pathParameters']['gid']
        user_id = event['pathParameters']['uid']
        
        group_members_table.delete_item(
            Key={
                'pk': f"TENANT#{user['tenant_id']}#GROUP#{group_id}",
                'sk': f"USER#{user_id}"
            }
        )
        
        # Write audit event
        write_audit_event(
            user['user_id'], user['tenant_id'], 'REMOVE_MEMBER',
            f"GROUP#{group_id}", {'target_user': user_id}
        )
        
        return {
            'statusCode': 204,
            'headers': cors_headers(),
            'body': ''
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Failed to remove member', 'detail': str(e)})
        }

def handle_analytics(event, user):
    """Get analytics overview"""
    try:
        query_params = event.get('queryStringParameters') or {}
        range_param = query_params.get('range', '7d')
        
        # Calculate date range
        days = {'1d': 1, '7d': 7, '30d': 30}.get(range_param, 7)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get settings count
        settings_response = settings_table.scan(
            FilterExpression='tenant_id = :tenant_id AND created_at >= :start_date',
            ExpressionAttributeValues={
                ':tenant_id': user['tenant_id'],
                ':start_date': start_date.isoformat()
            }
        )
        
        total_settings = settings_response['Count']
        public_settings = sum(1 for item in settings_response['Items'] if item.get('visibility') == 'public')
        
        # Get group members count
        members_response = group_members_table.query(
            IndexName='GSI2',
            KeyConditionExpression='gsi2_pk = :tenant_id',
            ExpressionAttributeValues={':tenant_id': f"TENANT#{user['tenant_id']}"}
        )
        
        total_members = members_response['Count']
        active_members = sum(1 for item in members_response['Items'] if item.get('status') == 'active')
        
        analytics_data = {
            'range': range_param,
            'total_settings': total_settings,
            'public_settings': public_settings,
            'private_settings': total_settings - public_settings,
            'total_members': total_members,
            'active_members': active_members,
            'inactive_members': total_members - active_members,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps(analytics_data, default=str)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Failed to get analytics', 'detail': str(e)})
        }

def handle_analytics_timeseries(event, user):
    """Get analytics timeseries data"""
    try:
        query_params = event.get('queryStringParameters') or {}
        metric = query_params.get('metric', 'settings')
        range_param = query_params.get('range', '7d')
        interval = query_params.get('interval', 'day')
        
        # Generate mock timeseries data
        days = {'1d': 1, '7d': 7, '30d': 30}.get(range_param, 7)
        
        timeseries = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i-1)
            value = 10 + (i * 2) + (i % 3)  # Mock data
            
            timeseries.append({
                'timestamp': date.isoformat(),
                'value': value,
                'metric': metric
            })
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'metric': metric,
                'range': range_param,
                'interval': interval,
                'data': timeseries
            }, default=str)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Failed to get timeseries', 'detail': str(e)})
        }
