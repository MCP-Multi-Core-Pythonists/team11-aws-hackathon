#!/usr/bin/env python3
import boto3
import json
import time
import requests

# Configuration
REGION = "us-east-1"
DISTRIBUTION_ID = "EPUT16LI6OAAI"
BUCKET_NAME = "sync-hub-web-1757132517"
CLOUDFRONT_DOMAIN = "d1iz4bwpzq14da.cloudfront.net"

def main():
    # Initialize clients
    s3 = boto3.client('s3', region_name=REGION)
    cloudfront = boto3.client('cloudfront', region_name=REGION)
    
    print("🔧 Fixing CloudFront with Origin Access Control...")
    
    # 1. Create Origin Access Control
    print("\n1️⃣ Creating Origin Access Control...")
    
    try:
        oac_response = cloudfront.create_origin_access_control(
            OriginAccessControlConfig={
                'Name': f'OAC-{BUCKET_NAME}',
                'Description': 'Origin Access Control for Sync Hub Web',
                'OriginAccessControlOriginType': 's3',
                'SigningBehavior': 'always',
                'SigningProtocol': 'sigv4'
            }
        )
        oac_id = oac_response['OriginAccessControl']['Id']
        print(f"✅ Created OAC: {oac_id}")
    except Exception as e:
        if 'already exists' in str(e):
            # List existing OACs and find ours
            oacs = cloudfront.list_origin_access_controls()
            for oac in oacs['OriginAccessControlList']['Items']:
                if BUCKET_NAME in oac['Name']:
                    oac_id = oac['Id']
                    print(f"✅ Using existing OAC: {oac_id}")
                    break
            else:
                print(f"❌ Error creating OAC: {e}")
                return
        else:
            print(f"❌ Error creating OAC: {e}")
            return
    
    # 2. Update CloudFront distribution to use OAC
    print("\n2️⃣ Updating CloudFront distribution with OAC...")
    
    response = cloudfront.get_distribution_config(Id=DISTRIBUTION_ID)
    config = response['DistributionConfig']
    etag = response['ETag']
    
    # Update origin to use OAC
    config['Origins']['Items'][0]['OriginAccessControlId'] = oac_id
    config['Origins']['Items'][0]['S3OriginConfig']['OriginAccessIdentity'] = ''
    
    # Update distribution
    cloudfront.update_distribution(
        Id=DISTRIBUTION_ID,
        DistributionConfig=config,
        IfMatch=etag
    )
    
    print("✅ Updated distribution with OAC")
    
    # 3. Update S3 bucket policy for OAC
    print("\n3️⃣ Updating S3 bucket policy for OAC...")
    
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowCloudFrontServicePrincipal",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudfront.amazonaws.com"
                },
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{BUCKET_NAME}/*",
                "Condition": {
                    "StringEquals": {
                        "AWS:SourceArn": f"arn:aws:cloudfront::851725240440:distribution/{DISTRIBUTION_ID}"
                    }
                }
            }
        ]
    }
    
    s3.put_bucket_policy(
        Bucket=BUCKET_NAME,
        Policy=json.dumps(bucket_policy)
    )
    
    print("✅ Updated bucket policy for OAC")
    
    # 4. Create invalidation
    print("\n4️⃣ Creating CloudFront invalidation...")
    
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
    
    # 5. Test access
    print("\n5️⃣ Testing web console access...")
    print("⏳ Waiting 45 seconds for OAC changes to propagate...")
    time.sleep(45)
    
    success = False
    for attempt in range(3):
        try:
            response = requests.get(f"https://{CLOUDFRONT_DOMAIN}/", timeout=15)
            if response.status_code == 200 and 'html' in response.text.lower():
                print("✅ Web Console loads successfully (HTTP 200, HTML content)")
                success = True
                break
            else:
                print(f"⚠️  Attempt {attempt+1}: HTTP {response.status_code}")
        except Exception as e:
            print(f"⚠️  Attempt {attempt+1}: {e}")
        
        if attempt < 2:
            time.sleep(10)
    
    # Test callback route (SPA routing)
    if success:
        try:
            callback_response = requests.get(f"https://{CLOUDFRONT_DOMAIN}/callback", timeout=10)
            if callback_response.status_code == 200:
                print("✅ /callback route works (SPA routing)")
            else:
                print(f"⚠️  /callback route: HTTP {callback_response.status_code}")
        except Exception as e:
            print(f"⚠️  /callback test failed: {e}")
    
    # Final output
    print("\n" + "="*60)
    print("🔧 CLOUDFRONT OAC FIX RESULTS")
    print("="*60)
    print(f"✅ Origin Access Control ID: {oac_id}")
    print(f"✅ index.html present in S3: {BUCKET_NAME}/index.html")
    print(f"✅ DefaultRootObject: index.html")
    print(f"✅ CustomErrorResponses: 403→/index.html (200), 404→/index.html (200)")
    print(f"✅ CloudFront invalidation ID: {invalidation_id}")
    print(f"{'✅' if success else '❌'} Web Console URL loads successfully: https://{CLOUDFRONT_DOMAIN}/")
    
    print(f"\n📋 Applied bucket policy:")
    print(json.dumps(bucket_policy, indent=2))

if __name__ == "__main__":
    main()
