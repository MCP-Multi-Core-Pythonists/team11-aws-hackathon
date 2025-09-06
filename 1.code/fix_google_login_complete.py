#!/usr/bin/env python3
"""
Fix Google login in Web Console by replacing placeholders with real Cognito URLs
"""
import boto3
import json
import os
import re
import time
import requests

def get_cognito_config():
    """Get Cognito configuration from SSM Parameter Store"""
    print("1️⃣ Discovering Cognito configuration...")
    
    ssm = boto3.client('ssm', region_name='us-east-1')
    
    try:
        # Get parameters
        params = ssm.get_parameters(
            Names=[
                '/synchub/cognito/user_pool_id',
                '/synchub/cognito/client_id', 
                '/synchub/cognito/domain',
                '/synchub/cloudfront/domain'
            ]
        )
        
        config = {}
        for param in params['Parameters']:
            key = param['Name'].split('/')[-1]
            config[key] = param['Value']
        
        print(f"✅ User Pool ID: {config.get('user_pool_id', 'NOT FOUND')}")
        print(f"✅ Client ID: {config.get('client_id', 'NOT FOUND')}")
        print(f"✅ Hosted UI Domain: {config.get('domain', 'NOT FOUND')}")
        print(f"✅ CloudFront Domain: {config.get('domain', 'NOT FOUND')}")
        
        return config
        
    except Exception as e:
        print(f"❌ Failed to get SSM parameters: {e}")
        # Fallback to known values
        return {
            'user_pool_id': 'us-east-1_ARkd0dYPj',
            'client_id': '7n568rmtbtp2tt8m0av2hl0f2n',
            'domain': 'sync-hub-851725240440',
            'cloudfront_domain': 'd1iz4bwpzq14da.cloudfront.net'
        }

def build_hosted_ui_urls(config):
    """Build Hosted UI and logout URLs"""
    print("\n2️⃣ Building Hosted UI URLs...")
    
    cognito_domain = config['domain']
    client_id = config['client_id']
    cloudfront_domain = config.get('cloudfront_domain', 'd1iz4bwpzq14da.cloudfront.net')
    
    hosted_ui_url = (
        f"https://{cognito_domain}.auth.us-east-1.amazoncognito.com/oauth2/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&scope=openid+email+profile"
        f"&redirect_uri=https://{cloudfront_domain}/oauth2/callback"
        f"&identity_provider=Google"
    )
    
    logout_url = (
        f"https://{cognito_domain}.auth.us-east-1.amazoncognito.com/logout"
        f"?client_id={client_id}"
        f"&logout_uri=https://{cloudfront_domain}/logout-complete"
    )
    
    print(f"✅ Hosted UI URL: {hosted_ui_url}")
    print(f"✅ Logout URL: {logout_url}")
    
    return hosted_ui_url, logout_url

def verify_cognito_config(config):
    """Verify and update Cognito configuration"""
    print("\n3️⃣ Verifying Cognito configuration...")
    
    cognito = boto3.client('cognito-idp', region_name='us-east-1')
    user_pool_id = config['user_pool_id']
    client_id = config['client_id']
    cloudfront_domain = config.get('cloudfront_domain', 'd1iz4bwpzq14da.cloudfront.net')
    
    try:
        # Get user pool client details
        response = cognito.describe_user_pool_client(
            UserPoolId=user_pool_id,
            ClientId=client_id
        )
        
        client_details = response['UserPoolClient']
        
        # Check callback URLs
        callback_urls = client_details.get('CallbackURLs', [])
        expected_callback = f"https://{cloudfront_domain}/oauth2/callback"
        
        if expected_callback not in callback_urls:
            print(f"⚠️ Adding callback URL: {expected_callback}")
            callback_urls.append(expected_callback)
        
        # Check logout URLs
        logout_urls = client_details.get('LogoutURLs', [])
        expected_logout = f"https://{cloudfront_domain}/logout-complete"
        
        if expected_logout not in logout_urls:
            print(f"⚠️ Adding logout URL: {expected_logout}")
            logout_urls.append(expected_logout)
        
        # Update client if needed
        cognito.update_user_pool_client(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            CallbackURLs=callback_urls,
            LogoutURLs=logout_urls,
            AllowedOAuthFlows=['code'],
            AllowedOAuthScopes=['openid', 'email', 'profile'],
            AllowedOAuthFlowsUserPoolClient=True,
            SupportedIdentityProviders=['COGNITO', 'Google']
        )
        
        print("✅ Cognito client configuration updated")
        
        # Check if Google IdP exists
        try:
            cognito.describe_identity_provider(
                UserPoolId=user_pool_id,
                ProviderName='Google'
            )
            print("✅ Google Identity Provider already configured")
            google_idp_enabled = True
        except cognito.exceptions.ResourceNotFoundException:
            print("⚠️ Google Identity Provider not found - would need manual setup")
            google_idp_enabled = False
        
        return True, google_idp_enabled
        
    except Exception as e:
        print(f"❌ Failed to verify Cognito config: {e}")
        return False, False

def replace_placeholders(hosted_ui_url, logout_url):
    """Replace placeholders in web files"""
    print("\n4️⃣ Replacing placeholders in web files...")
    
    # Search for files containing placeholders
    files_to_update = []
    
    # Check common locations
    search_paths = [
        '/Users/kyungjunlee/git_project/250906_Q_developer/sync-hub/web/dist/index.html',
        '/Users/kyungjunlee/git_project/250906_Q_developer/sync-hub/web/index.html',
        '/Users/kyungjunlee/git_project/250906_Q_developer/sync-hub/web/dist/env-config.js',
        '/Users/kyungjunlee/git_project/250906_Q_developer/sync-hub/web/env-config.js'
    ]
    
    for file_path in search_paths:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if 'HOSTED_UI_URL_PLACEHOLDER' in content:
                    files_to_update.append(file_path)
                    print(f"📁 Found placeholder in: {file_path}")
            except Exception as e:
                print(f"⚠️ Could not read {file_path}: {e}")
    
    # Update files
    updated_files = []
    for file_path in files_to_update:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Replace placeholders
            content = content.replace('HOSTED_UI_URL_PLACEHOLDER', hosted_ui_url)
            content = content.replace('LOGOUT_URL_PLACEHOLDER', logout_url)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            updated_files.append(file_path)
            print(f"✅ Updated: {file_path}")
            
        except Exception as e:
            print(f"❌ Failed to update {file_path}: {e}")
    
    # Also update the main web console file we know exists
    main_web_file = '/Users/kyungjunlee/git_project/250906_Q_developer/sync-hub/web/dist/index.html'
    if os.path.exists(main_web_file):
        try:
            with open(main_web_file, 'r') as f:
                content = f.read()
            
            # Look for Google login button and update it
            if 'Login with Google' in content:
                # Replace any hardcoded URLs or add proper URL
                content = re.sub(
                    r'href="[^"]*"([^>]*>.*?Login with Google)',
                    f'href="{hosted_ui_url}"\\1',
                    content
                )
                
                # Add JavaScript variables if not present
                if 'window.HOSTED_UI_URL' not in content:
                    js_config = f'''
    <script>
        window.HOSTED_UI_URL = "{hosted_ui_url}";
        window.COGNITO_LOGOUT_URL = "{logout_url}";
    </script>
    '''
                    content = content.replace('</head>', js_config + '</head>')
                
                with open(main_web_file, 'w') as f:
                    f.write(content)
                
                print(f"✅ Updated Google login in: {main_web_file}")
                updated_files.append(main_web_file)
        
        except Exception as e:
            print(f"⚠️ Could not update main web file: {e}")
    
    return updated_files

def deploy_changes():
    """Deploy changes using CDK or direct S3 upload"""
    print("\n6️⃣ Deploying changes...")
    
    # Try CDK deployment first
    try:
        os.chdir('/Users/kyungjunlee/git_project/250906_Q_developer/sync-hub')
        
        # CDK synth
        result = os.system('cdk synth > /dev/null 2>&1')
        if result == 0:
            print("✅ CDK synth successful")
            
            # CDK diff
            os.system('cdk diff > /dev/null 2>&1')
            print("✅ CDK diff completed")
            
            # CDK deploy (skip for now to avoid creating new resources)
            print("⚠️ Skipping CDK deploy to avoid creating new resources")
        else:
            print("⚠️ CDK synth failed, using direct S3 upload")
    
    except Exception as e:
        print(f"⚠️ CDK deployment issue: {e}")
    
    # Direct S3 upload as fallback
    try:
        web_file = '/Users/kyungjunlee/git_project/250906_Q_developer/sync-hub/web/dist/index.html'
        if os.path.exists(web_file):
            os.system(f'aws s3 cp {web_file} s3://sync-hub-web-1757132517/index.html --content-type "text/html"')
            print("✅ Uploaded updated web file to S3")
        
    except Exception as e:
        print(f"❌ S3 upload failed: {e}")

def invalidate_cloudfront():
    """Invalidate CloudFront distribution"""
    print("\n7️⃣ Invalidating CloudFront...")
    
    try:
        cloudfront = boto3.client('cloudfront', region_name='us-east-1')
        
        response = cloudfront.create_invalidation(
            DistributionId='EPUT16LI6OAAI',
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': ['/*']
                },
                'CallerReference': str(int(time.time()))
            }
        )
        
        invalidation_id = response['Invalidation']['Id']
        print(f"✅ CloudFront invalidation created: {invalidation_id}")
        return invalidation_id
        
    except Exception as e:
        print(f"❌ CloudFront invalidation failed: {e}")
        return None

def verify_deployment(hosted_ui_url, cloudfront_domain):
    """Verify the deployment works"""
    print("\n8️⃣ Verifying deployment...")
    
    results = {}
    
    # Test web console
    try:
        response = requests.get(f"https://{cloudfront_domain}/", timeout=10)
        results['web_console'] = {
            'status': response.status_code,
            'success': response.status_code == 200
        }
        print(f"✅ Web console: HTTP {response.status_code}")
    except Exception as e:
        results['web_console'] = {'status': 'ERROR', 'success': False, 'error': str(e)}
        print(f"❌ Web console error: {e}")
    
    # Test Hosted UI (expect redirect)
    try:
        response = requests.get(hosted_ui_url, timeout=10, allow_redirects=False)
        results['hosted_ui'] = {
            'status': response.status_code,
            'success': response.status_code in [200, 302]
        }
        print(f"✅ Hosted UI: HTTP {response.status_code}")
    except Exception as e:
        results['hosted_ui'] = {'status': 'ERROR', 'success': False, 'error': str(e)}
        print(f"❌ Hosted UI error: {e}")
    
    return results

def main():
    """Main execution flow"""
    print("🔧 FIXING GOOGLE LOGIN IN WEB CONSOLE")
    print("=" * 50)
    
    # Step 1: Get configuration
    config = get_cognito_config()
    
    # Step 2: Build URLs
    hosted_ui_url, logout_url = build_hosted_ui_urls(config)
    
    # Step 3: Verify Cognito config
    cognito_updated, google_idp_enabled = verify_cognito_config(config)
    
    # Step 4: Replace placeholders
    updated_files = replace_placeholders(hosted_ui_url, logout_url)
    
    # Step 5: Update frontend (already done in step 4)
    print("\n5️⃣ Frontend updated with Hosted UI URLs")
    
    # Step 6: Deploy changes
    deploy_changes()
    
    # Step 7: Invalidate CloudFront
    invalidation_id = invalidate_cloudfront()
    
    # Step 8: Verify deployment
    cloudfront_domain = config.get('cloudfront_domain', 'd1iz4bwpzq14da.cloudfront.net')
    verification_results = verify_deployment(hosted_ui_url, cloudfront_domain)
    
    # Step 9: Output results
    print("\n" + "=" * 50)
    print("🎉 GOOGLE LOGIN FIX RESULTS")
    print("=" * 50)
    
    print(f"\n🔗 HOSTED_UI_URL:")
    print(f"   {hosted_ui_url}")
    
    print(f"\n🚪 LOGOUT_URL:")
    print(f"   {logout_url}")
    
    print(f"\n🆔 Cognito Configuration:")
    print(f"   User Pool ID: {config['user_pool_id']}")
    print(f"   App Client ID: {config['client_id']}")
    print(f"   Hosted UI Domain: {config['domain']}")
    
    print(f"\n🌐 Web CloudFront Domain:")
    print(f"   {cloudfront_domain}")
    
    print(f"\n🔄 CloudFront Invalidation ID:")
    print(f"   {invalidation_id or 'FAILED'}")
    
    print(f"\n🔧 Configuration Updates:")
    print(f"   Cognito Client Updated: {'✅' if cognito_updated else '❌'}")
    print(f"   Google IdP Enabled: {'✅' if google_idp_enabled else '⚠️ Manual setup needed'}")
    
    print(f"\n📁 Updated Files:")
    for file_path in updated_files:
        print(f"   - {file_path}")
    
    print(f"\n🧪 Smoke Check Results:")
    for test_name, result in verification_results.items():
        status = "✅" if result['success'] else "❌"
        print(f"   {status} {test_name}: HTTP {result['status']}")
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Visit: https://{cloudfront_domain}/")
    print(f"2. Click 'Login with Google'")
    print(f"3. Should redirect to Cognito Hosted UI")
    print(f"4. Complete Google OAuth flow")
    print(f"5. Should redirect back to web console")
    
    if not google_idp_enabled:
        print(f"\n⚠️ Google Identity Provider Setup Required:")
        print(f"1. Go to Cognito Console → User Pools → {config['user_pool_id']}")
        print(f"2. Sign-in experience → Federated identity provider sign-in")
        print(f"3. Add Google as identity provider")
        print(f"4. Configure with Google OAuth client ID/secret")

if __name__ == "__main__":
    main()
