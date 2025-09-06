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
    
    print("🔧 Fixing CloudFront Web Console access...")
    
    # 1. Ensure index.html is in S3
    print("\n1️⃣ Checking S3 bucket contents...")
    
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key='index.html')
        print("✅ index.html found in S3")
    except:
        print("❌ index.html missing, uploading...")
        # Upload index.html if missing
        with open('web/index.html', 'r') as f:
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key='index.html',
                Body=f.read(),
                ContentType='text/html'
            )
        print("✅ index.html uploaded")
    
    # 2. Get current CloudFront distribution config
    print("\n2️⃣ Updating CloudFront distribution...")
    
    response = cloudfront.get_distribution_config(Id=DISTRIBUTION_ID)
    config = response['DistributionConfig']
    etag = response['ETag']
    
    # Update configuration
    config['DefaultRootObject'] = 'index.html'
    config['CustomErrorResponses'] = {
        'Quantity': 2,
        'Items': [
            {
                'ErrorCode': 403,
                'ResponsePagePath': '/index.html',
                'ResponseCode': '200',
                'ErrorCachingMinTTL': 300
            },
            {
                'ErrorCode': 404,
                'ResponsePagePath': '/index.html',
                'ResponseCode': '200',
                'ErrorCachingMinTTL': 300
            }
        ]
    }
    
    # Update distribution
    cloudfront.update_distribution(
        Id=DISTRIBUTION_ID,
        DistributionConfig=config,
        IfMatch=etag
    )
    
    print("✅ Updated DefaultRootObject: index.html")
    print("✅ Updated CustomErrorResponses: 403→index.html, 404→index.html")
    
    # 3. Fix S3 bucket policy for CloudFront access
    print("\n3️⃣ Configuring S3 bucket policy...")
    
    # Create bucket policy for CloudFront access
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
    
    # Apply bucket policy
    s3.put_bucket_policy(
        Bucket=BUCKET_NAME,
        Policy=json.dumps(bucket_policy)
    )
    
    print("✅ Applied bucket policy for CloudFront access")
    
    # 4. Create CloudFront invalidation
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
    
    # 5. Wait a moment and test
    print("\n5️⃣ Testing web console access...")
    print("⏳ Waiting 30 seconds for changes to propagate...")
    time.sleep(30)
    
    try:
        response = requests.get(f"https://{CLOUDFRONT_DOMAIN}/", timeout=10)
        if response.status_code == 200 and 'html' in response.text.lower():
            print("✅ Web Console loads successfully (HTTP 200, HTML content)")
            success = True
        else:
            print(f"⚠️  Web Console response: {response.status_code}")
            success = False
    except Exception as e:
        print(f"❌ Web Console test failed: {e}")
        success = False
    
    # Final output block
    print("\n" + "="*60)
    print("🔧 CLOUDFRONT FIX RESULTS")
    print("="*60)
    print(f"✅ index.html present in S3: {BUCKET_NAME}/index.html")
    print(f"✅ DefaultRootObject: index.html")
    print(f"✅ CustomErrorResponses: 403→/index.html (200), 404→/index.html (200)")
    print(f"✅ Bucket policy applied for CloudFront access")
    print(f"✅ CloudFront invalidation ID: {invalidation_id}")
    print(f"{'✅' if success else '⚠️'} Web Console URL: https://{CLOUDFRONT_DOMAIN}/")
    
    print(f"\n📋 Applied bucket policy:")
    print(json.dumps(bucket_policy, indent=2))

if __name__ == "__main__":
    main()
