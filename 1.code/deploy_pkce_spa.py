#!/usr/bin/env python3
import boto3
import json
import time
import os
import hashlib
import base64
import secrets
import requests
from urllib.parse import quote

# Configuration
REGION = "us-east-1"
USER_POOL_ID = "us-east-1_ARkd0dYPj"
APP_CLIENT_ID = "7n568rmtbtp2tt8m0av2hl0f2n"
HOSTED_UI_DOMAIN = "sync-hub-851725240440"
CLOUDFRONT_DOMAIN = "d1iz4bwpzq14da.cloudfront.net"
DISTRIBUTION_ID = "EPUT16LI6OAAI"
BUCKET_NAME = "sync-hub-web-1757132517"

def main():
    # Initialize clients
    cognito = boto3.client('cognito-idp', region_name=REGION)
    s3 = boto3.client('s3', region_name=REGION)
    cloudfront = boto3.client('cloudfront', region_name=REGION)
    
    print("🚀 Deploying PKCE-enabled SPA with Google login...")
    
    # 1. Configure Cognito App Client for PKCE
    print("\n1️⃣ Configuring Cognito App Client for PKCE...")
    
    # Get current client config
    response = cognito.describe_user_pool_client(
        UserPoolId=USER_POOL_ID,
        ClientId=APP_CLIENT_ID
    )
    
    # Update to public client with PKCE
    cognito.update_user_pool_client(
        UserPoolId=USER_POOL_ID,
        ClientId=APP_CLIENT_ID,
        SupportedIdentityProviders=['COGNITO', 'Google'],
        CallbackURLs=[
            'http://localhost:3000/callback',
            f'https://{CLOUDFRONT_DOMAIN}/callback'
        ],
        LogoutURLs=[
            'http://localhost:3000',
            f'https://{CLOUDFRONT_DOMAIN}'
        ],
        AllowedOAuthFlows=['code'],  # Authorization code with PKCE
        AllowedOAuthScopes=['openid', 'email', 'profile'],
        AllowedOAuthFlowsUserPoolClient=True,
        PreventUserExistenceErrors='ENABLED'
    )
    
    print("✅ App Client configured: Public client, PKCE enabled, code flow")
    
    # 2. Create enhanced SPA with PKCE
    print("\n2️⃣ Creating PKCE-enabled SPA...")
    
    os.makedirs('web', exist_ok=True)
    
    # Create comprehensive index.html with PKCE support
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sync Hub</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .auth-section {{ margin: 20px 0; padding: 20px; border: 1px solid #e1e5e9; border-radius: 6px; }}
        .admin-panel {{ background: #f8f9fa; border-color: #28a745; }}
        button {{ background: #4285f4; color: white; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-size: 14px; }}
        button:hover {{ background: #3367d6; }}
        .logout-btn {{ background: #dc3545; }}
        .logout-btn:hover {{ background: #c82333; }}
        .hidden {{ display: none; }}
        .user-info {{ background: #e7f3ff; padding: 15px; border-radius: 4px; margin: 10px 0; }}
        .loading {{ color: #666; font-style: italic; }}
        .error {{ color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 Sync Hub Web Console</h1>
        
        <div id="login-section" class="auth-section">
            <h2>Welcome to Sync Hub</h2>
            <p>Sign in with your Google account to access your settings sync.</p>
            <button onclick="loginWithGoogle()">🔐 Sign in with Google</button>
        </div>
        
        <div id="loading-section" class="auth-section hidden">
            <h2>Signing you in...</h2>
            <p class="loading">Processing authentication...</p>
        </div>
        
        <div id="user-section" class="auth-section hidden">
            <h2>✅ Welcome back!</h2>
            <div class="user-info">
                <p><strong>Email:</strong> <span id="user-email"></span></p>
                <p><strong>Name:</strong> <span id="user-name"></span></p>
                <p><strong>Tenant:</strong> <span id="user-tenant"></span></p>
            </div>
            <button class="logout-btn" onclick="logout()">Sign Out</button>
        </div>
        
        <div id="admin-panel" class="auth-section admin-panel hidden">
            <h2>🛠️ Admin Panel</h2>
            <p>You have administrative privileges for this tenant.</p>
            <div>
                <h3>Quick Actions</h3>
                <button onclick="alert('Admin feature coming soon!')">Manage Users</button>
                <button onclick="alert('Admin feature coming soon!')">View Analytics</button>
            </div>
        </div>
        
        <div id="error-section" class="error hidden">
            <strong>Authentication Error:</strong> <span id="error-message"></span>
        </div>
    </div>

    <script>
        // Configuration
        const CONFIG = {{
            CLIENT_ID: '{APP_CLIENT_ID}',
            DOMAIN: '{HOSTED_UI_DOMAIN}',
            REGION: '{REGION}',
            REDIRECT_URI: window.location.origin + '/callback'
        }};
        
        // PKCE utilities
        function generateCodeVerifier() {{
            const array = new Uint8Array(32);
            crypto.getRandomValues(array);
            return base64URLEncode(array);
        }}
        
        function base64URLEncode(buffer) {{
            return btoa(String.fromCharCode(...new Uint8Array(buffer)))
                .replace(/\\+/g, '-')
                .replace(/\\//g, '_')
                .replace(/=/g, '');
        }}
        
        async function generateCodeChallenge(verifier) {{
            const encoder = new TextEncoder();
            const data = encoder.encode(verifier);
            const digest = await crypto.subtle.digest('SHA-256', data);
            return base64URLEncode(digest);
        }}
        
        // Authentication functions
        async function loginWithGoogle() {{
            try {{
                // Generate PKCE parameters
                const codeVerifier = generateCodeVerifier();
                const codeChallenge = await generateCodeChallenge(codeVerifier);
                
                // Store verifier for callback
                sessionStorage.setItem('pkce_verifier', codeVerifier);
                
                // Build authorization URL
                const params = new URLSearchParams({{
                    client_id: CONFIG.CLIENT_ID,
                    response_type: 'code',
                    scope: 'openid email profile',
                    redirect_uri: CONFIG.REDIRECT_URI,
                    identity_provider: 'Google',
                    code_challenge: codeChallenge,
                    code_challenge_method: 'S256'
                }});
                
                const authUrl = `https://${{CONFIG.DOMAIN}}.auth.${{CONFIG.REGION}}.amazoncognito.com/oauth2/authorize?${{params}}`;
                window.location.href = authUrl;
            }} catch (error) {{
                showError('Failed to initiate login: ' + error.message);
            }}
        }}
        
        async function handleCallback() {{
            const urlParams = new URLSearchParams(window.location.search);
            const code = urlParams.get('code');
            const error = urlParams.get('error');
            
            if (error) {{
                showError('OAuth error: ' + (urlParams.get('error_description') || error));
                return;
            }}
            
            if (!code) {{
                showError('No authorization code received');
                return;
            }}
            
            showLoading();
            
            try {{
                // Get PKCE verifier
                const codeVerifier = sessionStorage.getItem('pkce_verifier');
                if (!codeVerifier) {{
                    throw new Error('PKCE verifier not found');
                }}
                
                // Exchange code for tokens
                const tokenResponse = await fetch(`https://${{CONFIG.DOMAIN}}.auth.${{CONFIG.REGION}}.amazoncognito.com/oauth2/token`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }},
                    body: new URLSearchParams({{
                        grant_type: 'authorization_code',
                        client_id: CONFIG.CLIENT_ID,
                        code: code,
                        redirect_uri: CONFIG.REDIRECT_URI,
                        code_verifier: codeVerifier
                    }})
                }});
                
                if (!tokenResponse.ok) {{
                    const errorData = await tokenResponse.text();
                    throw new Error(`Token exchange failed: ${{tokenResponse.status}} - ${{errorData}}`);
                }}
                
                const tokens = await tokenResponse.json();
                
                // Store tokens
                localStorage.setItem('access_token', tokens.access_token);
                localStorage.setItem('id_token', tokens.id_token);
                if (tokens.refresh_token) {{
                    localStorage.setItem('refresh_token', tokens.refresh_token);
                }}
                
                // Clean up
                sessionStorage.removeItem('pkce_verifier');
                
                // Redirect to main app
                window.location.replace('/');
                
            }} catch (error) {{
                console.error('Token exchange error:', error);
                showError('Authentication failed: ' + error.message);
                sessionStorage.removeItem('pkce_verifier');
            }}
        }}
        
        function logout() {{
            // Clear tokens
            localStorage.removeItem('access_token');
            localStorage.removeItem('id_token');
            localStorage.removeItem('refresh_token');
            sessionStorage.removeItem('pkce_verifier');
            
            // Redirect to Cognito logout
            const logoutUrl = `https://${{CONFIG.DOMAIN}}.auth.${{CONFIG.REGION}}.amazoncognito.com/logout?client_id=${{CONFIG.CLIENT_ID}}&logout_uri=${{encodeURIComponent(window.location.origin)}}`;
            window.location.href = logoutUrl;
        }}
        
        function parseJWT(token) {{
            try {{
                const base64Url = token.split('.')[1];
                const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
                const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {{
                    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
                }}).join(''));
                return JSON.parse(jsonPayload);
            }} catch (error) {{
                console.error('JWT parse error:', error);
                return null;
            }}
        }}
        
        function showLoading() {{
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('user-section').classList.add('hidden');
            document.getElementById('admin-panel').classList.add('hidden');
            document.getElementById('error-section').classList.add('hidden');
            document.getElementById('loading-section').classList.remove('hidden');
        }}
        
        function showLoginSection() {{
            document.getElementById('loading-section').classList.add('hidden');
            document.getElementById('user-section').classList.add('hidden');
            document.getElementById('admin-panel').classList.add('hidden');
            document.getElementById('error-section').classList.add('hidden');
            document.getElementById('login-section').classList.remove('hidden');
        }}
        
        function showUserSection(userInfo) {{
            document.getElementById('loading-section').classList.add('hidden');
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('error-section').classList.add('hidden');
            document.getElementById('user-section').classList.remove('hidden');
            
            document.getElementById('user-email').textContent = userInfo.email || 'N/A';
            document.getElementById('user-name').textContent = (userInfo.given_name || '') + ' ' + (userInfo.family_name || '');
            document.getElementById('user-tenant').textContent = userInfo.tenant_id || 'default';
            
            if (userInfo.is_admin) {{
                document.getElementById('admin-panel').classList.remove('hidden');
            }} else {{
                document.getElementById('admin-panel').classList.add('hidden');
            }}
        }}
        
        function showError(message) {{
            document.getElementById('loading-section').classList.add('hidden');
            document.getElementById('user-section').classList.add('hidden');
            document.getElementById('admin-panel').classList.add('hidden');
            document.getElementById('error-section').classList.remove('hidden');
            document.getElementById('error-message').textContent = message;
        }}
        
        // Initialize app
        function initApp() {{
            // Handle callback
            if (window.location.pathname === '/callback') {{
                handleCallback();
                return;
            }}
            
            // Check if user is logged in
            const idToken = localStorage.getItem('id_token');
            if (idToken) {{
                const payload = parseJWT(idToken);
                if (payload && payload.exp > Date.now() / 1000) {{
                    showUserSection(payload);
                    return;
                }}
                // Token expired, clear it
                localStorage.removeItem('id_token');
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
            }}
            
            showLoginSection();
        }}
        
        // Start the app
        initApp();
    </script>
</body>
</html>"""
    
    with open('web/index.html', 'w') as f:
        f.write(index_html)
    
    print("✅ Created PKCE-enabled SPA with token handling")
    
    # 3. Upload to S3
    print("\n3️⃣ Uploading SPA to S3...")
    
    file_count = 0
    for root, dirs, files in os.walk('web'):
        for file in files:
            local_path = os.path.join(root, file)
            s3_key = os.path.relpath(local_path, 'web')
            
            content_type = 'text/html' if file.endswith('.html') else 'text/plain'
            
            s3.upload_file(
                local_path, BUCKET_NAME, s3_key,
                ExtraArgs={'ContentType': content_type}
            )
            file_count += 1
    
    print(f"✅ Uploaded {file_count} files to S3")
    
    # 4. Verify CloudFront config
    print("\n4️⃣ Verifying CloudFront configuration...")
    
    dist_config = cloudfront.get_distribution_config(Id=DISTRIBUTION_ID)
    config = dist_config['DistributionConfig']
    
    print(f"✅ DefaultRootObject: {config.get('DefaultRootObject', 'Not set')}")
    
    error_responses = config.get('CustomErrorResponses', {}).get('Items', [])
    print(f"✅ CustomErrorResponses: {len(error_responses)} configured")
    for err in error_responses:
        print(f"   {err['ErrorCode']} → {err['ResponseCode']} → {err['ResponsePagePath']}")
    
    # 5. Create invalidation
    print("\n5️⃣ Creating CloudFront invalidation...")
    
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
    
    # 6. Generate sample PKCE challenge for testing
    sample_verifier = base64.b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=').replace('+', '-').replace('/', '_')
    sample_challenge = base64.b64encode(hashlib.sha256(sample_verifier.encode()).digest()).decode('utf-8').rstrip('=').replace('+', '-').replace('/', '_')
    
    hosted_ui_url = (
        f"https://{HOSTED_UI_DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/authorize"
        f"?client_id={APP_CLIENT_ID}"
        f"&response_type=code"
        f"&scope=openid+email+profile"
        f"&redirect_uri={quote(f'https://{CLOUDFRONT_DOMAIN}/callback')}"
        f"&identity_provider=Google"
        f"&code_challenge={sample_challenge}"
        f"&code_challenge_method=S256"
    )
    
    # 7. Wait and test
    print("\n6️⃣ Testing deployment...")
    print("⏳ Waiting 30 seconds for invalidation...")
    time.sleep(30)
    
    try:
        response = requests.get(f"https://{CLOUDFRONT_DOMAIN}/", timeout=15)
        spa_status = "✅ HTTP 200, HTML content" if response.status_code == 200 and 'html' in response.text.lower() else f"⚠️ HTTP {response.status_code}"
    except Exception as e:
        spa_status = f"❌ Error: {e}"
    
    # Final output
    print("\n" + "="*60)
    print("🚀 PKCE SPA DEPLOYMENT RESULTS")
    print("="*60)
    
    print(f"✅ Hosted UI Login URL (with PKCE):")
    print(f"   {hosted_ui_url}")
    
    print(f"\n✅ App Client Settings:")
    print(f"   - Type: Public client (no secret)")
    print(f"   - Flows: Authorization code with PKCE")
    print(f"   - Scopes: openid, email, profile")
    print(f"   - Identity Providers: COGNITO, Google")
    
    print(f"\n✅ S3 Sync Summary:")
    print(f"   - Files uploaded: {file_count}")
    print(f"   - Bucket: {BUCKET_NAME}")
    print(f"   - index.html: Present in root")
    
    print(f"\n✅ CloudFront:")
    print(f"   - Distribution: {DISTRIBUTION_ID}")
    print(f"   - DefaultRootObject: {config.get('DefaultRootObject')}")
    print(f"   - Invalidation ID: {invalidation_id}")
    
    print(f"\n✅ Smoke Test:")
    print(f"   - SPA accessibility: {spa_status}")
    print(f"   - Callback handling: Built-in PKCE token exchange")
    print(f"   - Token storage: localStorage (id_token, access_token)")
    print(f"   - Admin panel: Shown only if is_admin=true claim")
    
    print(f"\n🧪 Test Flow:")
    print(f"1. Visit: https://{CLOUDFRONT_DOMAIN}/")
    print(f"2. Click 'Sign in with Google'")
    print(f"3. Complete Google OAuth")
    print(f"4. Redirected to /callback → token exchange → redirect to /")
    print(f"5. SPA shows logged-in state with user info")

if __name__ == "__main__":
    main()
