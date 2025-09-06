#!/usr/bin/env python3
import requests
import json

# Configuration
API_BASE_URL = "https://l7ycatge3j.execute-api.us-east-1.amazonaws.com"
SETTING_ID = "test_setting_123"  # Replace with actual setting ID
JWT_TOKEN = "YOUR_JWT_TOKEN_HERE"  # Replace with actual JWT token

def test_tags_api():
    """Smoke test for tags API endpoints"""
    
    headers = {
        'Authorization': f'Bearer {JWT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    print("🧪 Testing Tags API endpoints...")
    
    # Test 1: POST tags (add tags)
    print("\n1️⃣ Testing POST /settings/{id}/tags...")
    
    post_data = {
        "items": ["dark", "vscode", "editor"]
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/settings/{SETTING_ID}/tags",
            headers=headers,
            json=post_data,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result}")
            print("   ✅ POST tags successful")
        else:
            print(f"   ⚠️ POST failed: {response.text}")
    
    except Exception as e:
        print(f"   ❌ POST error: {e}")
    
    # Test 2: GET tags
    print("\n2️⃣ Testing GET /settings/{id}/tags...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/settings/{SETTING_ID}/tags",
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result}")
            tags = result.get('items', [])
            if 'dark' in tags and 'vscode' in tags:
                print("   ✅ GET tags successful - contains expected tags")
            else:
                print("   ⚠️ GET tags - missing expected tags")
        else:
            print(f"   ⚠️ GET failed: {response.text}")
    
    except Exception as e:
        print(f"   ❌ GET error: {e}")
    
    # Test 3: DELETE tags (remove specific tags)
    print("\n3️⃣ Testing DELETE /settings/{id}/tags...")
    
    delete_data = {
        "items": ["dark"]
    }
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/settings/{SETTING_ID}/tags",
            headers=headers,
            json=delete_data,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result}")
            tags = result.get('items', [])
            if 'dark' not in tags and 'vscode' in tags:
                print("   ✅ DELETE tags successful - 'dark' removed, others remain")
            else:
                print("   ⚠️ DELETE tags - unexpected result")
        else:
            print(f"   ⚠️ DELETE failed: {response.text}")
    
    except Exception as e:
        print(f"   ❌ DELETE error: {e}")
    
    # Test 4: Verify final state
    print("\n4️⃣ Final verification GET /settings/{id}/tags...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/settings/{SETTING_ID}/tags",
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Final tags: {result.get('items', [])}")
            print("   ✅ Final verification complete")
        else:
            print(f"   ⚠️ Final GET failed: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Final GET error: {e}")
    
    print("\n📋 Test Summary:")
    print("   - POST tags: Add multiple tags to setting")
    print("   - GET tags: Retrieve all tags for setting")
    print("   - DELETE tags: Remove specific tags")
    print("   - Final GET: Verify remaining tags")
    
    print(f"\n🔗 Swagger UI: https://d1iz4bwpzq14da.cloudfront.net/docs/")
    print("   Navigate to '/settings/{id}/tags' section to see the new endpoints")

if __name__ == "__main__":
    if JWT_TOKEN == "YOUR_JWT_TOKEN_HERE":
        print("⚠️ Please update JWT_TOKEN and SETTING_ID in the script before running tests")
        print("   1. Get a JWT token from Cognito Hosted UI")
        print("   2. Create a setting first to get a valid SETTING_ID")
        print("   3. Update the variables in this script")
    else:
        test_tags_api()
