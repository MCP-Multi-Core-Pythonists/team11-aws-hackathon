#!/usr/bin/env python3
import boto3
import json
import requests
from urllib.parse import quote

# Configuration
REGION = "us-east-1"
USER_POOL_ID = "us-east-1_ARkd0dYPj"
APP_CLIENT_ID = "7n568rmtbtp2tt8m0av2hl0f2n"
HOSTED_UI_DOMAIN = "sync-hub-851725240440"
CLOUDFRONT_DOMAIN = "d1iz4bwpzq14da.cloudfront.net"

def main():
    cognito = boto3.client('cognito-idp', region_name=REGION)
    
    print("🔍 Verifying Google federated login configuration...")
    
    # 1. Check Google IdP configuration
    print("\n1️⃣ Checking Google Identity Provider...")
    
    try:
        idp_response = cognito.describe_identity_provider(
            UserPoolId=USER_POOL_ID,
            ProviderName='Google'
        )
        
        idp = idp_response['IdentityProvider']
        google_client_id = idp['ProviderDetails']['client_id']
        scopes = idp['ProviderDetails']['authorize_scopes']
        
        print(f"✅ Google IdP configured")
        print(f"   Client ID: {google_client_id[:12]}...{google_client_id[-12:]}")
        print(f"   Scopes: {scopes}")
        print(f"   Attribute mapping: {idp['AttributeMapping']}")
        
    except Exception as e:
        print(f"❌ Google IdP not found: {e}")
        return
    
    # 2. Check App Client configuration
    print("\n2️⃣ Checking App Client configuration...")
    
    try:
        client_response = cognito.describe_user_pool_client(
            UserPoolId=USER_POOL_ID,
            ClientId=APP_CLIENT_ID
        )
        
        client = client_response['UserPoolClient']
        supported_idps = client.get('SupportedIdentityProviders', [])
        callback_urls = client.get('CallbackURLs', [])
        logout_urls = client.get('LogoutURLs', [])
        
        print(f"✅ App Client configured")
        print(f"   Supported IdPs: {supported_idps}")
        print(f"   Callback URLs: {callback_urls}")
        print(f"   Logout URLs: {logout_urls}")
        
        # Verify Google is enabled
        if 'Google' not in supported_idps:
            print("⚠️  Adding Google to supported IdPs...")
            cognito.update_user_pool_client(
                UserPoolId=USER_POOL_ID,
                ClientId=APP_CLIENT_ID,
                SupportedIdentityProviders=['COGNITO', 'Google'],
                CallbackURLs=callback_urls,
                LogoutURLs=logout_urls,
                AllowedOAuthFlows=client['AllowedOAuthFlows'],
                AllowedOAuthScopes=client['AllowedOAuthScopes'],
                AllowedOAuthFlowsUserPoolClient=client['AllowedOAuthFlowsUserPoolClient']
            )
            print("✅ Added Google to supported IdPs")
        
    except Exception as e:
        print(f"❌ App Client error: {e}")
        return
    
    # 3. Generate and test Hosted UI URL
    print("\n3️⃣ Testing Hosted UI accessibility...")
    
    hosted_ui_url = (
        f"https://{HOSTED_UI_DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/authorize"
        f"?client_id={APP_CLIENT_ID}"
        f"&response_type=code"
        f"&scope=openid+email+profile"
        f"&redirect_uri={quote(f'https://{CLOUDFRONT_DOMAIN}/callback')}"
        f"&identity_provider=Google"
    )
    
    try:
        # Test if Hosted UI is accessible
        response = requests.get(f"https://{HOSTED_UI_DOMAIN}.auth.{REGION}.amazoncognito.com/login", timeout=10)
        if response.status_code == 200:
            print("✅ Hosted UI domain accessible")
        else:
            print(f"⚠️  Hosted UI response: {response.status_code}")
    except Exception as e:
        print(f"❌ Hosted UI test failed: {e}")
    
    # 4. Test web console
    print("\n4️⃣ Testing web console...")
    
    try:
        web_response = requests.get(f"https://{CLOUDFRONT_DOMAIN}/", timeout=10)
        if web_response.status_code == 200 and 'html' in web_response.text.lower():
            print("✅ Web console accessible")
            
            # Test callback route
            callback_response = requests.get(f"https://{CLOUDFRONT_DOMAIN}/callback", timeout=10)
            if callback_response.status_code == 200:
                print("✅ Callback route accessible (SPA routing works)")
            else:
                print(f"⚠️  Callback route: {callback_response.status_code}")
        else:
            print(f"⚠️  Web console: {web_response.status_code}")
    except Exception as e:
        print(f"❌ Web console test failed: {e}")
    
    # 5. Final output block
    print("\n" + "="*60)
    print("🔧 GOOGLE LOGIN CONFIGURATION SUMMARY")
    print("="*60)
    
    print(f"✅ Google CLIENT_ID: {google_client_id[:12]}...{google_client_id[-12:]}")
    print(f"✅ Google Redirect URI: https://{HOSTED_UI_DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/idpresponse")
    print(f"✅ Cognito Google IdP: Configured with scopes ({scopes})")
    print(f"✅ App Client enabled IdPs: {supported_idps}")
    
    print(f"\n🔗 Final Hosted UI URL:")
    print(hosted_ui_url)
    
    print(f"\n📋 Callback URLs configured:")
    for url in callback_urls:
        print(f"  - {url}")
    
    print(f"\n📋 Logout URLs configured:")
    for url in logout_urls:
        print(f"  - {url}")
    
    print(f"\n🧪 Smoke Test Steps:")
    print(f"1. Visit: {hosted_ui_url}")
    print(f"2. Should redirect to Google OAuth")
    print(f"3. After Google login, redirects to: https://{CLOUDFRONT_DOMAIN}/callback?code=...")
    print(f"4. Web console should show logged-in state")
    
    print(f"\n🔍 Google Cloud Console Requirements:")
    print(f"✅ OAuth 2.0 Client ID: {google_client_id}")
    print(f"✅ Authorized redirect URI: https://{HOSTED_UI_DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/idpresponse")
    print(f"✅ Test user (if in Testing): kyungjunlee.me@gmail.com")
    
    print(f"\n⚠️  If you get 'invalid_client' error:")
    print(f"1. Verify Google Client ID matches in Google Cloud Console")
    print(f"2. Ensure redirect URI is exactly: https://{HOSTED_UI_DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/idpresponse")
    print(f"3. Check OAuth consent screen is configured")
    print(f"4. Add test user or publish to production")

if __name__ == "__main__":
    main()
