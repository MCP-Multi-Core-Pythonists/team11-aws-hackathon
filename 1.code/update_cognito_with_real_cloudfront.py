#!/usr/bin/env python3
import boto3
import sys

# Configuration
USER_POOL_ID = "us-east-1_ARkd0dYPj"
CLIENT_ID = "7n568rmtbtp2tt8m0av2hl0f2n"
REGION = "us-east-1"

def main():
    if len(sys.argv) > 1:
        cloudfront_domain = sys.argv[1]
        print(f"🎯 Using provided CloudFront domain: {cloudfront_domain}")
    else:
        # Try to auto-detect
        cloudfront = boto3.client('cloudfront', region_name=REGION)
        distributions = cloudfront.list_distributions()
        items = distributions.get('DistributionList', {}).get('Items', [])
        
        if not items:
            print("❌ No CloudFront distributions found and no domain provided")
            print("Usage: python3 update_cognito_with_real_cloudfront.py <cloudfront-domain>")
            print("Example: python3 update_cognito_with_real_cloudfront.py d1a2b3c4d5e6f7.cloudfront.net")
            return
        
        cloudfront_domain = items[0]['DomainName']
        print(f"✅ Auto-detected CloudFront domain: {cloudfront_domain}")
    
    # Update Cognito
    cognito = boto3.client('cognito-idp', region_name=REGION)
    
    # Get current settings
    response = cognito.describe_user_pool_client(
        UserPoolId=USER_POOL_ID,
        ClientId=CLIENT_ID
    )
    client_config = response['UserPoolClient']
    
    # Update URLs
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
        ClientId=CLIENT_ID,
        CallbackURLs=updated_callbacks,
        LogoutURLs=updated_logouts,
        SupportedIdentityProviders=client_config['SupportedIdentityProviders'],
        AllowedOAuthFlows=client_config['AllowedOAuthFlows'],
        AllowedOAuthScopes=client_config['AllowedOAuthScopes'],
        AllowedOAuthFlowsUserPoolClient=client_config['AllowedOAuthFlowsUserPoolClient']
    )
    
    # Results
    user_pool_domain = "sync-hub-851725240440"
    hosted_ui_url = (
        f"https://{user_pool_domain}.auth.{REGION}.amazoncognito.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}&response_type=code&scope=email+openid+profile"
        f"&redirect_uri=https://{cloudfront_domain}/callback&identity_provider=Google"
    )
    
    print(f"\n✅ Updated Cognito App Client with CloudFront domain: {cloudfront_domain}")
    print(f"✅ Redirect URIs: {updated_callbacks}")
    print(f"✅ Logout URIs: {updated_logouts}")
    print(f"✅ Hosted UI URL: {hosted_ui_url}")

if __name__ == "__main__":
    main()
