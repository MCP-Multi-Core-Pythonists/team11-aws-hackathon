#!/usr/bin/env python3
"""
Bootstrap script to create Terraform backend resources (S3 bucket and DynamoDB table)
Run this once before initializing Terraform.
"""
import boto3
import json

def create_terraform_backend():
    """Create S3 bucket and DynamoDB table for Terraform backend"""
    
    # Configuration
    REGION = "us-east-1"
    ACCOUNT_ID = "851725240440"
    BUCKET_NAME = f"sync-hub-tfstate-{ACCOUNT_ID}-{REGION}"
    DYNAMODB_TABLE = "tfstate-locks"
    
    # Initialize AWS clients
    s3 = boto3.client('s3', region_name=REGION)
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    
    print("🚀 Creating Terraform backend resources...")
    
    # Create S3 bucket for state
    try:
        print(f"\n1️⃣ Creating S3 bucket: {BUCKET_NAME}")
        s3.create_bucket(Bucket=BUCKET_NAME)
        
        # Enable versioning
        s3.put_bucket_versioning(
            Bucket=BUCKET_NAME,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        
        # Enable server-side encryption
        s3.put_bucket_encryption(
            Bucket=BUCKET_NAME,
            ServerSideEncryptionConfiguration={
                'Rules': [{
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    }
                }]
            }
        )
        
        # Block public access
        s3.put_public_access_block(
            Bucket=BUCKET_NAME,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        
        print(f"✅ S3 bucket created: {BUCKET_NAME}")
        
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"✅ S3 bucket already exists: {BUCKET_NAME}")
    except Exception as e:
        print(f"❌ Error creating S3 bucket: {e}")
        return False
    
    # Create DynamoDB table for state locking
    try:
        print(f"\n2️⃣ Creating DynamoDB table: {DYNAMODB_TABLE}")
        dynamodb.create_table(
            TableName=DYNAMODB_TABLE,
            KeySchema=[
                {
                    'AttributeName': 'LockID',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'LockID',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {'Key': 'app', 'Value': 'sync-hub'},
                {'Key': 'env', 'Value': 'dev'},
                {'Key': 'managed_by', 'Value': 'terraform'}
            ]
        )
        
        # Wait for table to be active
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=DYNAMODB_TABLE)
        
        print(f"✅ DynamoDB table created: {DYNAMODB_TABLE}")
        
    except dynamodb.exceptions.ResourceInUseException:
        print(f"✅ DynamoDB table already exists: {DYNAMODB_TABLE}")
    except Exception as e:
        print(f"❌ Error creating DynamoDB table: {e}")
        return False
    
    print("\n✅ Terraform backend resources created successfully!")
    print(f"\nBackend configuration:")
    print(f"  S3 Bucket: {BUCKET_NAME}")
    print(f"  DynamoDB Table: {DYNAMODB_TABLE}")
    print(f"  Region: {REGION}")
    
    return True

if __name__ == "__main__":
    success = create_terraform_backend()
    if success:
        print("\n🎉 Ready to run 'terraform init'!")
    else:
        print("\n❌ Bootstrap failed. Please check the errors above.")
        exit(1)
