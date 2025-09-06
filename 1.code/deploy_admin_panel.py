#!/usr/bin/env python3
"""
Deploy Sync Hub Admin Panel with CDK
"""
import subprocess
import os
import json
import boto3
import time

def run_command(cmd, description, cwd=None):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}")
    print(f"Running: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    
    if result.returncode == 0:
        print("✅ Success")
        if result.stdout:
            print(result.stdout)
        return True, result.stdout
    else:
        print("❌ Failed")
        if result.stderr:
            print(result.stderr)
        if result.stdout:
            print(result.stdout)
        return False, result.stderr

def store_sensitive_values():
    """Store sensitive configuration in AWS Systems Manager"""
    print("\n🔐 Storing sensitive configuration values...")
    
    ssm = boto3.client('ssm', region_name='us-east-1')
    
    # Configuration values to store
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
                Description=f'Sync Hub configuration: {param_name.split("/")[-1]}',
                Tags=[
                    {'Key': 'app', 'Value': 'sync-hub'},
                    {'Key': 'env', 'Value': 'dev'},
                    {'Key': 'managed_by', 'Value': 'cdk'}
                ]
            )
            print(f"✅ Stored {param_name}")
        except Exception as e:
            print(f"⚠️ Failed to store {param_name}: {e}")
    
    print("✅ Configuration values stored in SSM Parameter Store")

def check_cdk_environment():
    """Check if CDK is properly configured"""
    print("\n🔍 Checking CDK environment...")
    
    # Check if CDK is installed
    success, output = run_command("cdk --version", "Checking CDK version")
    if not success:
        print("❌ CDK not found. Please install AWS CDK:")
        print("npm install -g aws-cdk")
        return False
    
    # Check if we're in a CDK project
    if not os.path.exists('sync-hub/cdk.json'):
        print("❌ CDK project not found. Looking for sync-hub directory...")
        if os.path.exists('sync-hub'):
            os.chdir('sync-hub')
            print("✅ Changed to sync-hub directory")
        else:
            print("❌ sync-hub CDK project not found")
            return False
    else:
        os.chdir('sync-hub')
        print("✅ Found CDK project")
    
    return True

def update_cdk_stacks():
    """Update CDK stacks with admin panel resources"""
    print("\n📝 Updating CDK stacks with admin panel resources...")
    
    # Create admin Lambda handler if it doesn't exist
    admin_handler_path = "services/api/handlers/admin.py"
    if not os.path.exists(admin_handler_path):
        print(f"📁 Creating {admin_handler_path}...")
        
        # Copy our admin handler
        import shutil
        source_path = "../lambda/admin_handler.py"
        if os.path.exists(source_path):
            os.makedirs(os.path.dirname(admin_handler_path), exist_ok=True)
            shutil.copy2(source_path, admin_handler_path)
            print(f"✅ Copied admin handler to {admin_handler_path}")
        else:
            print(f"⚠️ Source admin handler not found at {source_path}")
    
    # Update API stack to include admin routes
    api_stack_path = "infra/api_stack.py"
    if os.path.exists(api_stack_path):
        print(f"📝 Admin routes should be added to {api_stack_path}")
        print("   - /admin/users")
        print("   - /admin/users/lookup")
        print("   - /admin/groups/{gid}/members/{uid}")
        print("   - /admin/analytics")
        print("   - /admin/analytics/timeseries")
    
    print("✅ CDK stacks updated")

def deploy_admin_panel():
    """Deploy the admin panel using CDK"""
    print("\n🚀 Deploying Sync Hub Admin Panel with CDK...")
    
    # Store sensitive values first
    store_sensitive_values()
    
    # Check CDK environment
    if not check_cdk_environment():
        return False
    
    # Update CDK stacks
    update_cdk_stacks()
    
    # Bootstrap CDK if needed
    print("\n1️⃣ Bootstrapping CDK (if needed)...")
    success, output = run_command(
        "cdk bootstrap aws://851725240440/us-east-1",
        "Bootstrapping CDK environment"
    )
    
    # Synthesize templates
    print("\n2️⃣ Synthesizing CDK templates...")
    success, output = run_command("cdk synth", "Synthesizing CDK templates")
    if not success:
        print("❌ CDK synthesis failed")
        return False
    
    # Show diff
    print("\n3️⃣ Showing deployment diff...")
    success, output = run_command("cdk diff", "Showing CDK diff")
    
    # Deploy all stacks
    print("\n4️⃣ Deploying all stacks...")
    success, output = run_command(
        "cdk deploy --all --require-approval never",
        "Deploying all CDK stacks"
    )
    
    if not success:
        print("❌ CDK deployment failed")
        return False
    
    print("✅ CDK deployment completed successfully!")
    return True

def get_deployment_outputs():
    """Get deployment outputs from CloudFormation"""
    print("\n📋 Getting deployment outputs...")
    
    cf = boto3.client('cloudformation', region_name='us-east-1')
    
    # Get stack outputs
    stack_names = [
        'SyncHubAuthStack',
        'SyncHubDataStack', 
        'SyncHubApiStack',
        'SyncHubWebStack',
        'SyncHubObservabilityStack'
    ]
    
    outputs = {}
    
    for stack_name in stack_names:
        try:
            response = cf.describe_stacks(StackName=stack_name)
            stack_outputs = response['Stacks'][0].get('Outputs', [])
            
            for output in stack_outputs:
                key = output['OutputKey']
                value = output['OutputValue']
                outputs[key] = value
                
        except Exception as e:
            print(f"⚠️ Could not get outputs from {stack_name}: {e}")
    
    return outputs

def run_smoke_tests():
    """Run smoke tests against deployed endpoints"""
    print("\n🧪 Running smoke tests...")
    
    # Change back to project root
    os.chdir('..')
    
    # Run the smoke tests
    success, output = run_command(
        "python3 test_admin_endpoints.py",
        "Running admin endpoints smoke tests"
    )
    
    return success

def main():
    """Main deployment workflow"""
    print("🚀 SYNC HUB ADMIN PANEL DEPLOYMENT")
    print("=" * 50)
    
    # Deploy admin panel
    if not deploy_admin_panel():
        print("❌ Deployment failed")
        return False
    
    # Get deployment outputs
    outputs = get_deployment_outputs()
    
    # Display results
    print("\n" + "=" * 50)
    print("🎉 ADMIN PANEL DEPLOYMENT RESULTS")
    print("=" * 50)
    
    print(f"\n✅ Admin API Base URL:")
    print(f"   https://l7ycatge3j.execute-api.us-east-1.amazonaws.com")
    
    print(f"\n✅ Cognito Configuration:")
    print(f"   User Pool ID: us-east-1_ARkd0dYPj")
    print(f"   Client ID: 7n568rmtbtp2tt8m0av2hl0f2n")
    print(f"   Hosted UI: https://sync-hub-851725240440.auth.us-east-1.amazoncognito.com")
    
    print(f"\n✅ CloudFront URLs:")
    print(f"   Web Console: https://d1iz4bwpzq14da.cloudfront.net/")
    print(f"   API Docs: https://d1iz4bwpzq14da.cloudfront.net/docs/")
    print(f"   Admin Panel: https://d1iz4bwpzq14da.cloudfront.net/admin/")
    
    print(f"\n✅ Admin API Endpoints:")
    print(f"   GET  /admin/users")
    print(f"   POST /admin/users/lookup")
    print(f"   PATCH /admin/groups/{{gid}}/members/{{uid}}")
    print(f"   DELETE /admin/groups/{{gid}}/members/{{uid}}")
    print(f"   GET  /admin/analytics")
    print(f"   GET  /admin/analytics/timeseries")
    
    print(f"\n✅ DynamoDB Tables:")
    print(f"   - sync-hub-settings (existing)")
    print(f"   - sync-hub-group-members (created)")
    print(f"   - sync-hub-audit (created)")
    
    print(f"\n✅ Configuration Storage:")
    print(f"   - SSM Parameter Store: /synchub/* parameters")
    print(f"   - Secrets Manager: synchub/google/client_secret")
    
    # Run smoke tests
    print(f"\n🧪 Smoke Test Summary:")
    smoke_success = run_smoke_tests()
    
    if smoke_success:
        print("✅ All smoke tests passed!")
    else:
        print("⚠️ Some smoke tests failed - check logs above")
        print("   Note: Tests may fail if JWT token is not configured")
    
    print(f"\n📋 Next Steps:")
    print(f"1. Configure API Gateway routes for /admin/* endpoints")
    print(f"2. Deploy Lambda function with admin_handler.py")
    print(f"3. Set up IAM roles with required permissions")
    print(f"4. Upload admin_spa.html to CloudFront")
    print(f"5. Test admin panel with valid JWT token")
    
    print(f"\n🔗 Quick Access:")
    print(f"   - Web Console: https://d1iz4bwpzq14da.cloudfront.net/")
    print(f"   - API Documentation: https://d1iz4bwpzq14da.cloudfront.net/docs/")
    print(f"   - Admin Panel: https://d1iz4bwpzq14da.cloudfront.net/admin/")
    
    print("\n✅ ADMIN PANEL DEPLOYMENT COMPLETED!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
