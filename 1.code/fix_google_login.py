#!/usr/bin/env python3
import boto3
import json
import base64
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
    
    print("🔧 Fixing Google federated login for Cognito...")
    
    # Step 1: Instructions for Google Cloud Console
    print("\n1️⃣ Google Cloud Console Setup Required:")
    print("="*50)
    print("📋 Manual steps needed in Google Cloud Console:")
    print("1. Go to https://console.cloud.google.com/apis/credentials")
    print("2. Configure OAuth consent screen (External/Internal)")
    print("3. Add test user: kyungjunlee.me@gmail.com (if Testing)")
    print("4. Create OAuth 2.0 Client (Web application)")
    print("5. Add Authorized redirect URI:")
    print(f"   https://{HOSTED_UI_DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/idpresponse")
    print("6. Copy CLIENT_ID and CLIENT_SECRET")
    print()
    
    # Get Google credentials from user
    print("🔑 Enter your Google OAuth credentials:")
    google_client_id = input("Google CLIENT_ID: ").strip()
    google_client_secret = input("Google CLIENT_SECRET: ").strip()
    
    if not google_client_id or not google_client_secret:
        print("❌ Google credentials required. Exiting.")
        return
    
    # Step 2: Update Cognito Google IdP
    print("\n2️⃣ Updating Cognito Google Identity Provider...")
    
    try:
        # Update existing Google IdP
        cognito.update_identity_provider(
            UserPoolId=USER_POOL_ID,
            ProviderName='Google',
            ProviderDetails={
                'client_id': google_client_id,
                'client_secret': google_client_secret,
                'authorize_scopes': 'openid email profile'
            },
            AttributeMapping={
                'email': 'email',
                'given_name': 'given_name',
                'family_name': 'family_name'
            }
        )
        print("✅ Updated existing Google IdP")
    except Exception as e:
        if 'ResourceNotFoundException' in str(e):
            # Create new Google IdP
            cognito.create_identity_provider(
                UserPoolId=USER_POOL_ID,
                ProviderName='Google',
                ProviderType='Google',
                ProviderDetails={
                    'client_id': google_client_id,
                    'client_secret': google_client_secret,
                    'authorize_scopes': 'openid email profile'
                },
                AttributeMapping={
                    'email': 'email',
                    'given_name': 'given_name',
                    'family_name': 'family_name'
                }
            )
            print("✅ Created new Google IdP")
        else:
            print(f"❌ Error updating Google IdP: {e}")
            return
    
    # Step 3: Update App Client
    print("\n3️⃣ Updating App Client configuration...")
    
    # Get current app client config
    response = cognito.describe_user_pool_client(
        UserPoolId=USER_POOL_ID,
        ClientId=APP_CLIENT_ID
    )
    
    client_config = response['UserPoolClient']
    
    # Update app client with Google IdP
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
        AllowedOAuthFlows=client_config['AllowedOAuthFlows'],
        AllowedOAuthScopes=client_config['AllowedOAuthScopes'],
        AllowedOAuthFlowsUserPoolClient=client_config['AllowedOAuthFlowsUserPoolClient']
    )
    
    print("✅ Updated App Client with Google IdP")
    
    # Step 4: Generate final Hosted UI URL
    hosted_ui_url = (
        f"https://{HOSTED_UI_DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/authorize"
        f"?client_id={APP_CLIENT_ID}"
        f"&response_type=code"
        f"&scope=openid+email+profile"
        f"&redirect_uri={quote(f'https://{CLOUDFRONT_DOMAIN}/callback')}"
        f"&identity_provider=Google"
    )
    
    print(f"\n4️⃣ Final Hosted UI URL generated")
    
    # Step 5: Smoke test instructions
    print("\n5️⃣ Smoke Test Instructions:")
    print("="*40)
    print("1. Open the Hosted UI URL below")
    print("2. Click 'Continue with Google'")
    print("3. Complete Google OAuth flow")
    print("4. Verify redirect to /callback with authorization code")
    print("5. Check web console shows logged-in state")
    print()
    
    # Test basic connectivity
    try:
        test_response = requests.get(f"https://{CLOUDFRONT_DOMAIN}/", timeout=10)
        web_console_status = "✅ Accessible" if test_response.status_code == 200 else f"⚠️ HTTP {test_response.status_code}"
    except Exception as e:
        web_console_status = f"❌ Error: {e}"
    
    # Final output block
    print("\n" + "="*60)
    print("🔧 GOOGLE LOGIN FIX RESULTS")
    print("="*60)
    
    # Mask client ID for security
    masked_client_id = google_client_id[:8] + "..." + google_client_id[-4:] if len(google_client_id) > 12 else "***"
    
    print(f"✅ Google CLIENT_ID: {masked_client_id}")
    print(f"✅ Google Redirect URI: https://{HOSTED_UI_DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/idpresponse")
    print(f"✅ Cognito Google IdP: Configured with scopes (openid, email, profile)")
    print(f"✅ App Client enabled IdPs: ['COGNITO', 'Google']")
    print(f"✅ Web Console status: {web_console_status}")
    
    print(f"\n🔗 Final Hosted UI URL:")
    print(hosted_ui_url)
    
    print(f"\n📋 Callback URLs configured:")
    print(f"  - http://localhost:3000/callback")
    print(f"  - https://{CLOUDFRONT_DOMAIN}/callback")
    
    print(f"\n📋 Logout URLs configured:")
    print(f"  - http://localhost:3000")
    print(f"  - https://{CLOUDFRONT_DOMAIN}")
    
    print(f"\n🧪 Test the login flow:")
    print(f"1. Visit: {hosted_ui_url}")
    print(f"2. Click 'Continue with Google'")
    print(f"3. Complete OAuth → should redirect to: https://{CLOUDFRONT_DOMAIN}/callback?code=...")
    
    # Additional verification
    print(f"\n🔍 Verification steps:")
    print(f"- Check Google Cloud Console has redirect URI: https://{HOSTED_UI_DOMAIN}.auth.{REGION}.amazoncognito.com/oauth2/idpresponse")
    print(f"- Ensure OAuth consent screen is published or test user added")
    print(f"- Verify web console handles /callback route properly")

if __name__ == "__main__":
    main()
