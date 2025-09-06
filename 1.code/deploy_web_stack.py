#!/usr/bin/env python3
import boto3
import json
import time
import os
import subprocess
from urllib.parse import quote

# Configuration
REGION = "us-east-1"
API_BASE_URL = "https://l7ycatge3j.execute-api.us-east-1.amazonaws.com"
USER_POOL_ID = "us-east-1_ARkd0dYPj"
APP_CLIENT_ID = "7n568rmtbtp2tt8m0av2hl0f2n"
USER_POOL_DOMAIN = "sync-hub-851725240440"

def main():
    # Initialize clients
    cloudfront = boto3.client('cloudfront', region_name=REGION)
    s3 = boto3.client('s3', region_name=REGION)
    cognito = boto3.client('cognito-idp', region_name=REGION)
    
    print("🚀 Starting Sync Hub Web deployment...")
    
    # 1. Detect or create WebStack
    print("\n1️⃣ Checking for existing CloudFront distribution...")
    
    distributions = cloudfront.list_distributions()
    items = distributions.get('DistributionList', {}).get('Items', [])
    
    if items:
        # Use existing distribution
        dist = items[0]
        distribution_id = dist['Id']
        cloudfront_domain = dist['DomainName']
        
        # Find S3 bucket from distribution config
        dist_config = cloudfront.get_distribution_config(Id=distribution_id)
        origins = dist_config['DistributionConfig']['Origins']['Items']
        s3_origin = next((o for o in origins if 's3' in o['DomainName']), None)
        
        if s3_origin:
            web_bucket_name = s3_origin['DomainName'].split('.')[0]
        else:
            web_bucket_name = f"sync-hub-web-{int(time.time())}"
            
        print(f"✅ Found existing distribution: {distribution_id}")
        print(f"✅ CloudFront domain: {cloudfront_domain}")
        print(f"✅ Web bucket: {web_bucket_name}")
        
    else:
        # Create new WebStack
        print("📦 Creating new WebStack...")
        web_bucket_name = f"sync-hub-web-{int(time.time())}"
        
        # Create S3 bucket
        s3.create_bucket(Bucket=web_bucket_name)
        
        # Configure bucket for static website
        s3.put_bucket_website(
            Bucket=web_bucket_name,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'},
                'ErrorDocument': {'Key': 'index.html'}  # SPA routing
            }
        )
        
        # Create CloudFront distribution
        dist_config = {
            'CallerReference': str(int(time.time())),
            'Comment': 'Sync Hub Web Console',
            'DefaultRootObject': 'index.html',
            'Origins': {
                'Quantity': 1,
                'Items': [{
                    'Id': 'S3Origin',
                    'DomainName': f"{web_bucket_name}.s3.amazonaws.com",
                    'S3OriginConfig': {
                        'OriginAccessIdentity': ''
                    }
                }]
            },
            'DefaultCacheBehavior': {
                'TargetOriginId': 'S3Origin',
                'ViewerProtocolPolicy': 'redirect-to-https',
                'TrustedSigners': {
                    'Enabled': False,
                    'Quantity': 0
                },
                'ForwardedValues': {
                    'QueryString': False,
                    'Cookies': {'Forward': 'none'}
                },
                'MinTTL': 0
            },
            'CustomErrorResponses': {
                'Quantity': 1,
                'Items': [{
                    'ErrorCode': 404,
                    'ResponsePagePath': '/index.html',
                    'ResponseCode': '200',
                    'ErrorCachingMinTTL': 300
                }]
            },
            'Enabled': True
        }
        
        response = cloudfront.create_distribution(DistributionConfig=dist_config)
        distribution_id = response['Distribution']['Id']
        cloudfront_domain = response['Distribution']['DomainName']
        
        print(f"✅ Created distribution: {distribution_id}")
        print(f"✅ CloudFront domain: {cloudfront_domain}")
        print(f"✅ Web bucket: {web_bucket_name}")
    
    # 2. Create and upload SPA
    print("\n2️⃣ Creating and uploading SPA...")
    
    # Create web directory and files
    os.makedirs('web', exist_ok=True)
    
    # Create index.html
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sync Hub</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .auth-section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; }}
        .admin-panel {{ background: #f5f5f5; }}
        button {{ padding: 10px 20px; margin: 10px; cursor: pointer; }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Sync Hub Web Console</h1>
        
        <div id="login-section" class="auth-section">
            <h2>Login</h2>
            <button onclick="loginWithGoogle()">Login with Google</button>
        </div>
        
        <div id="user-section" class="auth-section hidden">
            <h2>Welcome!</h2>
            <p>User: <span id="user-email"></span></p>
            <button onclick="logout()">Logout</button>
        </div>
        
        <div id="admin-panel" class="auth-section admin-panel hidden">
            <h2>Admin Panel</h2>
            <p>Admin features available here</p>
        </div>
    </div>

    <script>
        const API_BASE = '{API_BASE_URL}';
        const CLIENT_ID = '{APP_CLIENT_ID}';
        const DOMAIN = '{USER_POOL_DOMAIN}';
        const REDIRECT_URI = window.location.origin + '/callback';
        
        function loginWithGoogle() {{
            const url = `https://${{DOMAIN}}.auth.us-east-1.amazoncognito.com/oauth2/authorize?client_id=${{CLIENT_ID}}&response_type=code&scope=email+openid+profile&redirect_uri=${{encodeURIComponent(REDIRECT_URI)}}&identity_provider=Google`;
            window.location.href = url;
        }}
        
        function logout() {{
            localStorage.removeItem('access_token');
            showLoginSection();
        }}
        
        function showLoginSection() {{
            document.getElementById('login-section').classList.remove('hidden');
            document.getElementById('user-section').classList.add('hidden');
            document.getElementById('admin-panel').classList.add('hidden');
        }}
        
        function showUserSection(userInfo) {{
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('user-section').classList.remove('hidden');
            document.getElementById('user-email').textContent = userInfo.email;
            
            if (userInfo.is_admin) {{
                document.getElementById('admin-panel').classList.remove('hidden');
            }}
        }}
        
        // Handle OAuth callback
        if (window.location.pathname === '/callback') {{
            const urlParams = new URLSearchParams(window.location.search);
            const code = urlParams.get('code');
            
            if (code) {{
                // Exchange code for tokens (simplified)
                fetch(`${{API_BASE}}/auth/token`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ code, redirect_uri: REDIRECT_URI }})
                }})
                .then(r => r.json())
                .then(data => {{
                    if (data.access_token) {{
                        localStorage.setItem('access_token', data.access_token);
                        window.location.href = '/';
                    }}
                }});
            }}
        }}
        
        // Check if user is logged in
        const token = localStorage.getItem('access_token');
        if (token) {{
            // Decode JWT to get user info (simplified)
            try {{
                const payload = JSON.parse(atob(token.split('.')[1]));
                showUserSection({{
                    email: payload.email,
                    is_admin: payload.is_admin || false
                }});
            }} catch (e) {{
                showLoginSection();
            }}
        }}
    </script>
</body>
</html>"""
    
    with open('web/index.html', 'w') as f:
        f.write(index_html)
    
    # Upload to S3
    for root, dirs, files in os.walk('web'):
        for file in files:
            local_path = os.path.join(root, file)
            s3_key = os.path.relpath(local_path, 'web')
            
            content_type = 'text/html' if file.endswith('.html') else 'text/plain'
            
            s3.upload_file(
                local_path, web_bucket_name, s3_key,
                ExtraArgs={'ContentType': content_type}
            )
    
    # Create CloudFront invalidation
    invalidation = cloudfront.create_invalidation(
        DistributionId=distribution_id,
        InvalidationBatch={
            'Paths': {'Quantity': 1, 'Items': ['/*']},
            'CallerReference': str(int(time.time()))
        }
    )
    invalidation_id = invalidation['Invalidation']['Id']
    print(f"✅ Created invalidation: {invalidation_id}")
    
    # 3. Update Cognito App Client
    print("\n3️⃣ Updating Cognito App Client...")
    
    # Check if script exists
    if os.path.exists('update_cognito_with_real_cloudfront.py'):
        subprocess.run(['python3', 'update_cognito_with_real_cloudfront.py', cloudfront_domain])
    else:
        # Update directly with boto3
        response = cognito.describe_user_pool_client(
            UserPoolId=USER_POOL_ID,
            ClientId=APP_CLIENT_ID
        )
        
        client_config = response['UserPoolClient']
        
        updated_callbacks = [
            "http://localhost:3000/callback",
            f"https://{cloudfront_domain}/callback"
        ]
        
        updated_logouts = [
            "http://localhost:3000",
            f"https://{cloudfront_domain}"
        ]
        
        cognito.update_user_pool_client(
            UserPoolId=USER_POOL_ID,
            ClientId=APP_CLIENT_ID,
            CallbackURLs=updated_callbacks,
            LogoutURLs=updated_logouts,
            SupportedIdentityProviders=client_config['SupportedIdentityProviders'],
            AllowedOAuthFlows=client_config['AllowedOAuthFlows'],
            AllowedOAuthScopes=client_config['AllowedOAuthScopes'],
            AllowedOAuthFlowsUserPoolClient=client_config['AllowedOAuthFlowsUserPoolClient']
        )
        
        print(f"✅ Updated redirect URIs: {updated_callbacks}")
        print(f"✅ Updated logout URIs: {updated_logouts}")
    
    # 4. Build Hosted UI Login URL
    hosted_ui_url = (
        f"https://{USER_POOL_DOMAIN}.auth.us-east-1.amazoncognito.com/oauth2/authorize"
        f"?client_id={APP_CLIENT_ID}"
        f"&response_type=code"
        f"&scope=email+openid+profile"
        f"&redirect_uri={quote(f'https://{cloudfront_domain}/callback')}"
        f"&identity_provider=Google"
    )
    
    print(f"\n4️⃣ HostedUILoginURL (Google, prod): {hosted_ui_url}")
    
    # 5. Smoke Tests
    print("\n5️⃣ Running smoke tests...")
    
    import requests
    
    try:
        health_response = requests.get(f"{API_BASE_URL}/_health", timeout=10)
        health_status = health_response.status_code
        print(f"✅ Health check: {health_status}")
    except Exception as e:
        health_status = f"Error: {e}"
        print(f"❌ Health check failed: {e}")
    
    try:
        settings_response = requests.get(f"{API_BASE_URL}/settings/public", timeout=10)
        print(f"✅ Public settings: {settings_response.status_code}")
    except Exception as e:
        print(f"❌ Public settings failed: {e}")
    
    print(f"\n📝 Admin endpoint example:")
    print(f"curl -X POST {API_BASE_URL}/admin/groups/GROUP_ID/members \\")
    print(f"  -H 'Authorization: Bearer ADMIN_JWT_TOKEN' \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{{'\"email\":\"user@example.com\",\"role\":\"member\"}}'")
    
    # 6. Final Output Block
    print("\n" + "="*60)
    print("🎉 FINAL OUTPUT BLOCK")
    print("="*60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"CloudFront Web URL: https://{cloudfront_domain}/")
    print(f"WebBucketName: {web_bucket_name}")
    print(f"DistributionId: {distribution_id}")
    print(f"Cognito:")
    print(f"  User Pool Id: {USER_POOL_ID}")
    print(f"  App Client Id: {APP_CLIENT_ID}")
    print(f"  Redirect URIs: ['http://localhost:3000/callback', 'https://{cloudfront_domain}/callback']")
    print(f"  Logout URIs: ['http://localhost:3000', 'https://{cloudfront_domain}']")
    print(f"HostedUILoginURL (Google, prod): {hosted_ui_url}")
    print(f"Health check: {health_status}")
    print(f"CloudFront invalidation ID: {invalidation_id}")

if __name__ == "__main__":
    main()
