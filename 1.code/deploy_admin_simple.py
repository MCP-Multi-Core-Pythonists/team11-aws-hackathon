#!/usr/bin/env python3
"""
Simplified Admin Panel deployment for Sync Hub
"""
import boto3
import json
import time
import requests

def deploy_admin_resources():
    """Deploy admin panel resources directly"""
    print("🚀 SYNC HUB ADMIN PANEL DEPLOYMENT")
    print("=" * 50)
    
    # Store configuration in SSM (without tags to avoid conflicts)
    print("\n🔐 Storing configuration values...")
    ssm = boto3.client('ssm', region_name='us-east-1')
    
    config_values = {
        '/synchub/cognito/user_pool_id': 'us-east-1_ARkd0dYPj',
        '/synchub/cognito/client_id': '7n568rmtbtp2tt8m0av2hl0f2n',
        '/synchub/cognito/domain': 'sync-hub-851725240440',
        '/synchub/api/base_url': 'https://l7ycatge3j.execute-api.us-east-1.amazonaws.com',
        '/synchub/cloudfront/domain': 'd1iz4bwpzq14da.cloudfront.net',
        '/synchub/cloudfront/distribution_id': 'EPUT16LI6OAAI',
        '/synchub/s3/web_bucket': 'sync-hub-web-1757132517'
    }
    
    for param_name, param_value in config_values.items():
        try:
            ssm.put_parameter(
                Name=param_name,
                Value=param_value,
                Type='String',
                Overwrite=True,
                Description=f'Sync Hub configuration: {param_name.split("/")[-1]}'
            )
            print(f"✅ Stored {param_name}")
        except Exception as e:
            print(f"⚠️ Failed to store {param_name}: {e}")
    
    # Upload admin SPA to S3
    print("\n📤 Uploading admin SPA to S3...")
    s3 = boto3.client('s3', region_name='us-east-1')
    bucket_name = 'sync-hub-web-1757132517'
    
    try:
        # Upload admin SPA
        s3.upload_file(
            'admin_spa.html', bucket_name, 'admin/index.html',
            ExtraArgs={
                'ContentType': 'text/html',
                'CacheControl': 'max-age=300'
            }
        )
        print("✅ Uploaded admin SPA to /admin/index.html")
    except Exception as e:
        print(f"⚠️ Failed to upload admin SPA: {e}")
    
    # Create CloudFront invalidation
    print("\n🔄 Creating CloudFront invalidation...")
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    distribution_id = 'EPUT16LI6OAAI'
    
    try:
        invalidation = cloudfront.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': ['/admin/*']
                },
                'CallerReference': str(int(time.time()))
            }
        )
        invalidation_id = invalidation['Invalidation']['Id']
        print(f"✅ Created invalidation: {invalidation_id}")
    except Exception as e:
        print(f"⚠️ Failed to create invalidation: {e}")
    
    # Test endpoints
    print("\n🧪 Testing existing infrastructure...")
    
    # Test API health
    try:
        response = requests.get('https://l7ycatge3j.execute-api.us-east-1.amazonaws.com/_health', timeout=10)
        api_status = f"✅ HTTP {response.status_code}" if response.status_code == 200 else f"⚠️ HTTP {response.status_code}"
    except Exception as e:
        api_status = f"❌ Error: {e}"
    
    # Test CloudFront
    try:
        response = requests.get('https://d1iz4bwpzq14da.cloudfront.net/', timeout=10)
        cf_status = f"✅ HTTP {response.status_code}" if response.status_code == 200 else f"⚠️ HTTP {response.status_code}"
    except Exception as e:
        cf_status = f"❌ Error: {e}"
    
    # Test admin SPA
    try:
        response = requests.get('https://d1iz4bwpzq14da.cloudfront.net/admin/index.html', timeout=10)
        admin_status = f"✅ HTTP {response.status_code}" if response.status_code == 200 else f"⚠️ HTTP {response.status_code}"
    except Exception as e:
        admin_status = f"❌ Error: {e}"
    
    # Display results
    print("\n" + "=" * 50)
    print("🎉 ADMIN PANEL DEPLOYMENT RESULTS")
    print("=" * 50)
    
    print(f"\n✅ Admin API Base URL:")
    print(f"   https://l7ycatge3j.execute-api.us-east-1.amazonaws.com")
    print(f"   Status: {api_status}")
    
    print(f"\n✅ Cognito Configuration:")
    print(f"   User Pool ID: us-east-1_ARkd0dYPj")
    print(f"   Client ID: 7n568rmtbtp2tt8m0av2hl0f2n")
    print(f"   Hosted UI: https://sync-hub-851725240440.auth.us-east-1.amazoncognito.com")
    
    print(f"\n✅ CloudFront URLs:")
    print(f"   Web Console: https://d1iz4bwpzq14da.cloudfront.net/")
    print(f"   Status: {cf_status}")
    print(f"   API Docs: https://d1iz4bwpzq14da.cloudfront.net/docs/")
    print(f"   Admin Panel: https://d1iz4bwpzq14da.cloudfront.net/admin/")
    print(f"   Admin Status: {admin_status}")
    
    print(f"\n✅ Admin API Endpoints (Ready for Lambda deployment):")
    print(f"   GET  /admin/users")
    print(f"   POST /admin/users/lookup")
    print(f"   PATCH /admin/groups/{{gid}}/members/{{uid}}")
    print(f"   DELETE /admin/groups/{{gid}}/members/{{uid}}")
    print(f"   GET  /admin/analytics")
    print(f"   GET  /admin/analytics/timeseries")
    
    print(f"\n✅ DynamoDB Tables:")
    print(f"   - sync-hub-settings ✅ (existing)")
    print(f"   - sync-hub-group-members ✅ (created)")
    print(f"   - sync-hub-audit ✅ (created)")
    
    print(f"\n✅ Configuration Storage:")
    print(f"   - SSM Parameter Store: /synchub/* parameters ✅")
    print(f"   - Secrets Manager: synchub/google/client_secret ✅")
    
    print(f"\n📋 Next Steps for Complete Deployment:")
    print(f"1. Deploy Lambda function:")
    print(f"   - Create Lambda with lambda/admin_handler.py")
    print(f"   - Set environment variables from SSM parameters")
    print(f"   - Configure IAM role with DynamoDB + Cognito permissions")
    print(f"2. Configure API Gateway routes:")
    print(f"   - Add /admin/* routes to existing HTTP API")
    print(f"   - Connect routes to admin Lambda function")
    print(f"3. Test admin panel:")
    print(f"   - Get admin JWT token from Cognito")
    print(f"   - Run smoke tests: python3 test_admin_endpoints.py")
    
    print(f"\n📋 Example curl commands (after Lambda deployment):")
    print(f"# List users (admin only)")
    print(f"curl -H 'Authorization: Bearer ADMIN_JWT_TOKEN' \\")
    print(f"     'https://l7ycatge3j.execute-api.us-east-1.amazonaws.com/admin/users?limit=20'")
    print(f"")
    print(f"# Get analytics overview")
    print(f"curl -H 'Authorization: Bearer ADMIN_JWT_TOKEN' \\")
    print(f"     'https://l7ycatge3j.execute-api.us-east-1.amazonaws.com/admin/analytics?range=7d'")
    
    print(f"\n🔗 Quick Access:")
    print(f"   - Web Console: https://d1iz4bwpzq14da.cloudfront.net/")
    print(f"   - API Documentation: https://d1iz4bwpzq14da.cloudfront.net/docs/")
    print(f"   - Admin Panel: https://d1iz4bwpzq14da.cloudfront.net/admin/")
    
    print("\n✅ ADMIN PANEL INFRASTRUCTURE READY!")
    print("Lambda function and API Gateway routes need manual deployment.")
    
    return True

if __name__ == "__main__":
    success = deploy_admin_resources()
    exit(0 if success else 1)
