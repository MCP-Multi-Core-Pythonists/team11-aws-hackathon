#!/usr/bin/env python3
"""
Create/update DynamoDB tables for Admin Panel features
"""
import boto3
import json

def create_admin_tables():
    """Create or update DynamoDB tables for admin features"""
    
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
    
    print("🗄️ Creating/updating DynamoDB tables for Admin Panel...")
    
    # 1. Group Members Table
    print("\n1️⃣ Creating group_members table...")
    try:
        dynamodb.create_table(
            TableName='sync-hub-group-members',
            KeySchema=[
                {'AttributeName': 'pk', 'KeyType': 'HASH'},
                {'AttributeName': 'sk', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'pk', 'AttributeType': 'S'},
                {'AttributeName': 'sk', 'AttributeType': 'S'},
                {'AttributeName': 'gsi1_pk', 'AttributeType': 'S'},
                {'AttributeName': 'gsi1_sk', 'AttributeType': 'S'},
                {'AttributeName': 'gsi2_pk', 'AttributeType': 'S'},
                {'AttributeName': 'gsi2_sk', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'GSI1',
                    'KeySchema': [
                        {'AttributeName': 'gsi1_pk', 'KeyType': 'HASH'},
                        {'AttributeName': 'gsi1_sk', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'GSI2',
                    'KeySchema': [
                        {'AttributeName': 'gsi2_pk', 'KeyType': 'HASH'},
                        {'AttributeName': 'gsi2_sk', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {'Key': 'app', 'Value': 'sync-hub'},
                {'Key': 'env', 'Value': 'dev'},
                {'Key': 'managed_by', 'Value': 'terraform'}
            ]
        )
        print("✅ Created sync-hub-group-members table")
    except dynamodb.exceptions.ResourceInUseException:
        print("✅ sync-hub-group-members table already exists")
    except Exception as e:
        print(f"❌ Error creating group_members table: {e}")
    
    # 2. Audit Table
    print("\n2️⃣ Creating audit table...")
    try:
        dynamodb.create_table(
            TableName='sync-hub-audit',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'tenant_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'TenantTimestampIndex',
                    'KeySchema': [
                        {'AttributeName': 'tenant_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {'Key': 'app', 'Value': 'sync-hub'},
                {'Key': 'env', 'Value': 'dev'},
                {'Key': 'managed_by', 'Value': 'terraform'}
            ]
        )
        print("✅ Created sync-hub-audit table")
    except dynamodb.exceptions.ResourceInUseException:
        print("✅ sync-hub-audit table already exists")
    except Exception as e:
        print(f"❌ Error creating audit table: {e}")
    
    # 3. Check existing settings table
    print("\n3️⃣ Checking settings table...")
    try:
        response = dynamodb.describe_table(TableName='sync-hub-settings')
        print("✅ sync-hub-settings table exists")
    except dynamodb.exceptions.ResourceNotFoundException:
        print("⚠️ sync-hub-settings table not found - creating...")
        try:
            dynamodb.create_table(
                TableName='sync-hub-settings',
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'tenant_id', 'AttributeType': 'S'},
                    {'AttributeName': 'created_at', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'TenantCreatedIndex',
                        'KeySchema': [
                            {'AttributeName': 'tenant_id', 'KeyType': 'HASH'},
                            {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {'Key': 'app', 'Value': 'sync-hub'},
                    {'Key': 'env', 'Value': 'dev'},
                    {'Key': 'managed_by', 'Value': 'terraform'}
                ]
            )
            print("✅ Created sync-hub-settings table")
        except Exception as e:
            print(f"❌ Error creating settings table: {e}")
    
    print("\n✅ DynamoDB tables setup completed!")
    
    # Print table schema summary
    print("\n📋 Table Schema Summary:")
    print("sync-hub-group-members:")
    print("  PK: TENANT#{tenant_id}#GROUP#{group_id}")
    print("  SK: USER#{user_id}")
    print("  GSI1: email -> TENANT#{tenant_id} (user lookup)")
    print("  GSI2: TENANT#{tenant_id} -> GROUP#{group_id} (analytics)")
    print("  Attributes: email, role, status, joined_at")
    print()
    print("sync-hub-audit:")
    print("  PK: AUDIT#{timestamp}#{user_id}")
    print("  GSI: tenant_id -> timestamp (audit log queries)")
    print("  Attributes: action, resource, details")
    print()
    print("sync-hub-settings:")
    print("  PK: id")
    print("  GSI: tenant_id -> created_at (analytics)")
    print("  Attributes: name, content, visibility, created_at")

if __name__ == "__main__":
    create_admin_tables()
