#!/usr/bin/env python3
"""
Smoke test for Sync Hub local development environment
"""
import os
import sys
import asyncio
from typing import Dict, Any

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE = os.getenv("API_BASE", "https://l7ycatge3j.execute-api.us-east-1.amazonaws.com")
COGNITO_DOMAIN = os.getenv("COGNITO_DOMAIN", "https://sync-hub-851725240440.auth.us-east-1.amazoncognito.com")
LOCAL_BASE = "http://localhost:3001"

async def test_endpoint(client: httpx.AsyncClient, url: str, description: str) -> Dict[str, Any]:
    """Test a single endpoint"""
    try:
        response = await client.get(url, timeout=10.0)
        return {
            "url": url,
            "description": description,
            "status": response.status_code,
            "success": response.status_code < 400,
            "response_size": len(response.content),
            "error": None
        }
    except Exception as e:
        return {
            "url": url,
            "description": description,
            "status": None,
            "success": False,
            "response_size": 0,
            "error": str(e)
        }

async def main():
    """Run smoke tests"""
    print("🧪 Running Sync Hub Local Development Smoke Tests")
    print("=" * 60)
    
    tests = [
        # Production API tests
        (f"{API_BASE}/_health", "Production API Health Check"),
        (f"{API_BASE}/settings/public", "Production API Public Settings"),
        
        # Cognito tests
        (f"{COGNITO_DOMAIN}/.well-known/jwks.json", "Cognito JWKS Endpoint"),
        
        # Local development server tests
        (f"{LOCAL_BASE}/health", "Local Dev Health Check"),
        (f"{LOCAL_BASE}/", "Local Dev Index Page"),
        (f"{LOCAL_BASE}/settings/public", "Local Dev Public Settings Proxy"),
    ]
    
    results = []
    
    async with httpx.AsyncClient() as client:
        for url, description in tests:
            print(f"Testing: {description}")
            result = await test_endpoint(client, url, description)
            results.append(result)
            
            if result["success"]:
                print(f"  ✅ {result['status']} - {result['response_size']} bytes")
            else:
                print(f"  ❌ {result['status']} - {result['error']}")
    
    print("\n" + "=" * 60)
    print("📊 SMOKE TEST SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    
    print(f"Tests passed: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed:")
        for result in results:
            if not result["success"]:
                print(f"  - {result['description']}: {result['error'] or result['status']}")
        return 1

    print(f"\n🔗 Local Development URLs:")
    print(f"  - Main page: {LOCAL_BASE}/")
    print(f"  - Login: {LOCAL_BASE}/login-start")
    print(f"  - Health: {LOCAL_BASE}/health")
    
    print(f"\n📋 Configuration:")
    print(f"  - API Base: {API_BASE}")
    print(f"  - Cognito Domain: {COGNITO_DOMAIN}")
    print(f"  - Local Server: {LOCAL_BASE}")

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
