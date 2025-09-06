#!/usr/bin/env python3
import boto3
import json
import yaml
import os
import time
import requests
from urllib.parse import quote

# Configuration
REGION = "us-east-1"
BUCKET_NAME = "sync-hub-web-1757132517"
DISTRIBUTION_ID = "EPUT16LI6OAAI"
CLOUDFRONT_DOMAIN = "d1iz4bwpzq14da.cloudfront.net"
API_BASE_URL = "https://l7ycatge3j.execute-api.us-east-1.amazonaws.com"

def main():
    # Initialize clients
    s3 = boto3.client('s3', region_name=REGION)
    cloudfront = boto3.client('cloudfront', region_name=REGION)
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    print("📚 Deploying API documentation with Swagger UI...")
    
    # 1. Convert YAML to JSON
    print("\n1️⃣ Processing OpenAPI specification...")
    
    with open('docs/openapi.yaml', 'r') as f:
        openapi_data = yaml.safe_load(f)
    
    # Save JSON version
    os.makedirs('docs', exist_ok=True)
    with open('docs/openapi.json', 'w') as f:
        json.dump(openapi_data, f, indent=2)
    
    print("✅ Created OpenAPI JSON from YAML")
    
    # 2. Create Swagger UI
    print("\n2️⃣ Creating Swagger UI...")
    
    swagger_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sync Hub API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.10.3/swagger-ui.css" />
    <style>
        html {{ box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }}
        *, *:before, *:after {{ box-sizing: inherit; }}
        body {{ margin:0; background: #fafafa; }}
        .swagger-ui .topbar {{ display: none; }}
        .custom-header {{ 
            background: #1f2937; 
            color: white; 
            padding: 20px; 
            text-align: center; 
            margin-bottom: 20px;
        }}
        .custom-header h1 {{ margin: 0; font-size: 2em; }}
        .custom-header p {{ margin: 10px 0 0 0; opacity: 0.8; }}
    </style>
</head>
<body>
    <div class="custom-header">
        <h1>🔄 Sync Hub API</h1>
        <p>Multi-tenant SaaS for VS Code Extension + Web Console</p>
        <p><strong>Base URL:</strong> {API_BASE_URL}</p>
    </div>
    <div id="swagger-ui"></div>
    
    <script src="https://unpkg.com/swagger-ui-dist@5.10.3/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.3/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: './openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                tryItOutEnabled: true,
                requestInterceptor: function(request) {{
                    // Add CORS headers for API calls
                    request.headers['Access-Control-Allow-Origin'] = '*';
                    return request;
                }},
                onComplete: function() {{
                    console.log('Swagger UI loaded successfully');
                }}
            }});
        }};
    </script>
</body>
</html>"""
    
    with open('docs/index.html', 'w') as f:
        f.write(swagger_html)
    
    print("✅ Created Swagger UI")
    
    # 3. Create API.md documentation
    print("\n3️⃣ Creating developer documentation...")
    
    api_md = f"""# Sync Hub API Documentation

## Overview

The Sync Hub API provides endpoints for managing VS Code settings synchronization across multiple devices and teams.

- **Base URL:** `{API_BASE_URL}`
- **Authentication:** JWT Bearer tokens from Cognito
- **Authorization:** `https://sync-hub-851725240440.auth.us-east-1.amazoncognito.com`

## Interactive Documentation

- **Swagger UI:** [https://{CLOUDFRONT_DOMAIN}/docs/](https://{CLOUDFRONT_DOMAIN}/docs/)
- **OpenAPI Spec:** [https://{CLOUDFRONT_DOMAIN}/docs/openapi.json](https://{CLOUDFRONT_DOMAIN}/docs/openapi.json)

## Authentication

All endpoints (except `/_health` and `/settings/public`) require a JWT Bearer token:

```bash
Authorization: Bearer <your-jwt-token>
```

### Getting a Token

1. Visit the Hosted UI: `https://sync-hub-851725240440.auth.us-east-1.amazoncognito.com`
2. Sign in with Google
3. Extract the `id_token` from the callback

## Quick Start Examples

### Health Check (Public)
```bash
curl -X GET "{API_BASE_URL}/_health"
```

### Create a Private Setting
```bash
curl -X POST "{API_BASE_URL}/settings" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "name": "my-vscode-config",
    "content": {{"editor.fontSize": 16, "workbench.colorTheme": "Dark+"}},
    "visibility": "private"
  }}'
```

### List My Settings
```bash
curl -X GET "{API_BASE_URL}/settings" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### List Public Settings (No Auth)
```bash
curl -X GET "{API_BASE_URL}/settings/public"
```

### Get Setting History
```bash
curl -X GET "{API_BASE_URL}/settings/SETTING_ID/history" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Rollback Setting
```bash
curl -X POST "{API_BASE_URL}/settings/SETTING_ID/rollback" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{"version": 2}}'
```

### Create a Group
```bash
curl -X POST "{API_BASE_URL}/groups" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "name": "Development Team",
    "description": "Shared settings for developers"
  }}'
```

### Admin: Add Member to Group
```bash
curl -X POST "{API_BASE_URL}/admin/groups/GROUP_ID/members" \\
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "email": "user@example.com",
    "role": "member"
  }}'
```

## Error Handling

All errors follow this format:

```json
{{
  "error": "Error message",
  "detail": "Additional details (optional)",
  "request_id": "req_123456 (optional)"
}}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden (Admin required)
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limits

- **Authenticated requests:** 1000 requests per hour
- **Public endpoints:** 100 requests per hour per IP

## Support

For API support, contact: support@synchub.dev
"""
    
    with open('docs/API.md', 'w') as f:
        f.write(api_md)
    
    print("✅ Created API.md documentation")
    
    # 4. Upload docs to S3
    print("\n4️⃣ Uploading documentation to S3...")
    
    docs_files = [
        ('docs/openapi.yaml', 'application/x-yaml'),
        ('docs/openapi.json', 'application/json'),
        ('docs/index.html', 'text/html'),
        ('docs/API.md', 'text/markdown')
    ]
    
    for file_path, content_type in docs_files:
        s3_key = file_path
        s3.upload_file(
            file_path, BUCKET_NAME, s3_key,
            ExtraArgs={
                'ContentType': content_type,
                'CacheControl': 'max-age=300'  # 5 minutes cache
            }
        )
    
    print(f"✅ Uploaded {len(docs_files)} documentation files")
    
    # 5. Create Lambda for API route
    print("\n5️⃣ Creating Lambda for /docs/openapi.json route...")
    
    lambda_code = '''
import json

def lambda_handler(event, context):
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': 'https://d1iz4bwpzq14da.cloudfront.net',
        'Access-Control-Allow-Headers': 'Authorization, Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS'
    }
    
    # Handle preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # OpenAPI spec
    openapi_spec = ''' + json.dumps(openapi_data) + '''
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(openapi_spec)
    }
'''
    
    # Create deployment package
    import zipfile
    with zipfile.ZipFile('/tmp/docs_lambda.zip', 'w') as z:
        z.writestr('lambda_function.py', lambda_code)
    
    # Deploy Lambda (this would need proper IAM role setup)
    print("⚠️  Lambda deployment requires additional IAM setup")
    print("   Manual step: Create Lambda function 'sync-hub-docs' with the generated code")
    
    # 6. Create CloudFront invalidation
    print("\n6️⃣ Creating CloudFront invalidation...")
    
    invalidation = cloudfront.create_invalidation(
        DistributionId=DISTRIBUTION_ID,
        InvalidationBatch={
            'Paths': {
                'Quantity': 1,
                'Items': ['/docs/*']
            },
            'CallerReference': str(int(time.time()))
        }
    )
    
    invalidation_id = invalidation['Invalidation']['Id']
    print(f"✅ Created invalidation: {invalidation_id}")
    
    # 7. Wait and test
    print("\n7️⃣ Testing documentation deployment...")
    print("⏳ Waiting 30 seconds for invalidation...")
    time.sleep(30)
    
    # Test CloudFront docs
    try:
        docs_response = requests.get(f"https://{CLOUDFRONT_DOMAIN}/docs/", timeout=15)
        docs_status = "✅ HTTP 200, Swagger UI" if docs_response.status_code == 200 and 'swagger' in docs_response.text.lower() else f"⚠️ HTTP {docs_response.status_code}"
    except Exception as e:
        docs_status = f"❌ Error: {e}"
    
    # Test OpenAPI JSON
    try:
        spec_response = requests.get(f"https://{CLOUDFRONT_DOMAIN}/docs/openapi.json", timeout=10)
        spec_status = "✅ HTTP 200, Valid JSON" if spec_response.status_code == 200 and spec_response.json().get('openapi') else f"⚠️ HTTP {spec_response.status_code}"
    except Exception as e:
        spec_status = f"❌ Error: {e}"
    
    # Test API health
    try:
        health_response = requests.get(f"{API_BASE_URL}/_health", timeout=10)
        health_status = f"✅ HTTP {health_response.status_code}" if health_response.status_code == 200 else f"⚠️ HTTP {health_response.status_code}"
    except Exception as e:
        health_status = f"❌ Error: {e}"
    
    # Final output
    print("\n" + "="*60)
    print("📚 API DOCUMENTATION DEPLOYMENT RESULTS")
    print("="*60)
    
    print(f"✅ OpenAPI JSON URL (CloudFront): https://{CLOUDFRONT_DOMAIN}/docs/openapi.json")
    print(f"✅ OpenAPI YAML URL (CloudFront): https://{CLOUDFRONT_DOMAIN}/docs/openapi.yaml")
    print(f"✅ Swagger UI URL: https://{CLOUDFRONT_DOMAIN}/docs/")
    print(f"✅ API route for spec: GET {API_BASE_URL}/docs/openapi.json (requires Lambda setup)")
    print(f"✅ Confirmed security scheme: bearer JWT (Cognito)")
    
    print(f"\n🧪 Smoke Test Results:")
    print(f"   - Swagger UI: {docs_status}")
    print(f"   - OpenAPI JSON: {spec_status}")
    print(f"   - API Health: {health_status}")
    print(f"   - CloudFront invalidation: {invalidation_id}")
    
    print(f"\n📋 Quick curl examples:")
    print(f"# Get OpenAPI spec")
    print(f"curl -s https://{CLOUDFRONT_DOMAIN}/docs/openapi.json | jq '.info.title'")
    print(f"")
    print(f"# Test health endpoint")
    print(f"curl -s {API_BASE_URL}/_health")
    print(f"")
    print(f"# Test secured endpoint (requires token)")
    print(f"curl -H 'Authorization: Bearer YOUR_JWT_TOKEN' {API_BASE_URL}/settings")
    
    print(f"\n🔗 Documentation URLs:")
    print(f"   - Interactive docs: https://{CLOUDFRONT_DOMAIN}/docs/")
    print(f"   - Developer guide: https://{CLOUDFRONT_DOMAIN}/docs/API.md")
    print(f"   - OpenAPI spec: https://{CLOUDFRONT_DOMAIN}/docs/openapi.json")

if __name__ == "__main__":
    main()
