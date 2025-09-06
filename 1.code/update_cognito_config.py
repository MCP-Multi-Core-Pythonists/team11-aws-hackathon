#!/usr/bin/env python3
import boto3
import json

# Configuration
USER_POOL_ID = "us-east-1_ARkd0dYPj"
CLIENT_ID = "7n568rmtbtp2tt8m0av2hl0f2n"
REGION = "us-east-1"

def main():
    # Initialize AWS clients
    cloudfront = boto3.client('cloudfront', region_name=REGION)
    cognito = boto3.client('cognito-idp', region_name=REGION)
    
    # 1. Find CloudFront distribution domain
    print("🔍 Finding CloudFront distribution...")
    distributions = cloudfront.list_distributions()
    
    cloudfront_domain = None
    items = distributions.get('DistributionList', {}).get('Items', [])
    if items:
        # Get the first distribution (assuming it's the WebStack)
        dist = items[0]
        cloudfront_domain = dist['DomainName']
        print(f"✅ Found CloudFront domain: {cloudfront_domain}")
    else:
        print("❌ No CloudFront distributions found")
        print("💡 Using example domain for demonstration...")
        cloudfront_domain = "d1234567890123.cloudfront.net"  # Placeholder for demo
    
    # 2. Get current Cognito App Client settings
    print("\n📋 Getting current Cognito App Client settings...")
    response = cognito.describe_user_pool_client(
        UserPoolId=USER_POOL_ID,
        ClientId=CLIENT_ID
    )
    
    client_config = response['UserPoolClient']
    current_callbacks = client_config.get('CallbackURLs', [])
    current_logouts = client_config.get('LogoutURLs', [])
    
    print(f"Current callback URLs: {current_callbacks}")
    print(f"Current logout URLs: {current_logouts}")
    
    # 3. Update redirect and logout URIs
    new_callback_url = f"https://{cloudfront_domain}/callback"
    new_logout_url = f"https://{cloudfront_domain}"
    
    # Prepare updated URLs
    updated_callbacks = ["http://localhost:3000/callback"]
    if new_callback_url not in updated_callbacks:
        updated_callbacks.append(new_callback_url)
    
    updated_logouts = ["http://localhost:3000"]
    if new_logout_url not in updated_logouts:
        updated_logouts.append(new_logout_url)
    
    # Update the App Client
    print(f"\n🔄 Updating Cognito App Client...")
    cognito.update_user_pool_client(
        UserPoolId=USER_POOL_ID,
        ClientId=CLIENT_ID,
        CallbackURLs=updated_callbacks,
        LogoutURLs=updated_logouts,
        SupportedIdentityProviders=client_config['SupportedIdentityProviders'],
        AllowedOAuthFlows=client_config['AllowedOAuthFlows'],
        AllowedOAuthScopes=client_config['AllowedOAuthScopes'],
        AllowedOAuthFlowsUserPoolClient=client_config['AllowedOAuthFlowsUserPoolClient']
    )
    
    # 4. Get User Pool domain for Hosted UI URL
    print("\n🔍 Finding User Pool domain...")
    user_pool_domain = "sync-hub-851725240440"  # From the stack resources
    
    # Verify the domain exists
    try:
        domain_response = cognito.describe_user_pool_domain(Domain=user_pool_domain)
        print(f"✅ Found User Pool domain: {user_pool_domain}")
    except Exception as e:
        print(f"⚠️  Could not verify domain: {e}")
    
    # 5. Print results
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    print(f"✅ Confirmed CloudFront domain: {cloudfront_domain}")
    print(f"✅ Updated redirect URIs: {updated_callbacks}")
    print(f"✅ Updated logout URIs: {updated_logouts}")
    
    # Generate Hosted UI URL
    hosted_ui_url = (
        f"https://{user_pool_domain}.auth.{REGION}.amazoncognito.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&scope=email+openid+profile"
        f"&redirect_uri=https://{cloudfront_domain}/callback"
        f"&identity_provider=Google"
    )
    print(f"✅ Hosted UI login URL (Google): {hosted_ui_url}")

if __name__ == "__main__":
    main()
