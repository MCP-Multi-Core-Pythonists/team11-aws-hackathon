import pytest
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

class TestAPI:
    def setup_method(self):
        """Setup for each test method"""
        self.base_url = BASE_URL
        self.test_user = {
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "password": "testpassword123",
            "name": "Test User"
        }
        self.auth_token = None

    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_public_health_check(self):
        """Test public health check endpoint"""
        response = requests.get(f"{self.base_url}/_health")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "ts" in data

    def test_user_registration(self):
        """Test user registration"""
        response = requests.post(
            f"{self.base_url}/auth/register",
            json=self.test_user
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Check if response has either user_id or user.id
        assert "user_id" in data or ("user" in data and "id" in data["user"])

    def test_user_login(self):
        """Test user login after registration"""
        # First register
        requests.post(f"{self.base_url}/auth/register", json=self.test_user)
        
        # Then login
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        
        # Store token for subsequent tests
        self.auth_token = data["access_token"]

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

    def test_get_user_profile(self):
        """Test getting user profile with authentication"""
        # Register and login first
        requests.post(f"{self.base_url}/auth/register", json=self.test_user)
        login_response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Get profile
        response = requests.get(
            f"{self.base_url}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == self.test_user["email"]
        assert "id" in data

    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        response = requests.get(f"{self.base_url}/users/me")
        assert response.status_code == 403  # Should be unauthorized

    def test_team_creation(self):
        """Test team creation"""
        # Register and login first
        requests.post(f"{self.base_url}/auth/register", json=self.test_user)
        login_response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Create team
        team_data = {
            "name": "Test Team",
            "description": "A test team",
            "is_public": False
        }
        response = requests.post(
            f"{self.base_url}/teams",
            json=team_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == team_data["name"]
        assert "id" in data

    def test_settings_sync(self):
        """Test settings synchronization"""
        # Register and login first
        requests.post(f"{self.base_url}/auth/register", json=self.test_user)
        login_response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Sync settings
        settings_data = {
            "settings": {
                "editor.fontSize": 14,
                "workbench.colorTheme": "Dark+"
            }
        }
        response = requests.post(
            f"{self.base_url}/settings/sync/apply",
            json=settings_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["applied_count"] == 2

    def test_bookmarks(self):
        """Test bookmark creation and retrieval"""
        # Register and login first
        requests.post(f"{self.base_url}/auth/register", json=self.test_user)
        login_response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Create bookmark
        bookmark_data = {
            "setting_id": "test-setting-id",
            "name": "Test Bookmark",
            "description": "A test bookmark",
            "tags": ["test", "bookmark"]
        }
        response = requests.post(
            f"{self.base_url}/bookmarks",
            json=bookmark_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == bookmark_data["name"]
        
        # Get bookmarks
        response = requests.get(
            f"{self.base_url}/bookmarks",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        bookmarks = response.json()
        assert len(bookmarks) >= 1

if __name__ == "__main__":
    # Run tests manually
    test_instance = TestAPI()
    
    print("🧪 Running API Tests...")
    
    try:
        test_instance.setup_method()
        test_instance.test_health_check()
        print("✅ Health check test passed")
        
        test_instance.setup_method()
        test_instance.test_public_health_check()
        print("✅ Public health check test passed")
        
        test_instance.setup_method()
        test_instance.test_user_registration()
        print("✅ User registration test passed")
        
        test_instance.setup_method()
        test_instance.test_user_login()
        print("✅ User login test passed")
        
        test_instance.setup_method()
        test_instance.test_invalid_login()
        print("✅ Invalid login test passed")
        
        test_instance.setup_method()
        test_instance.test_get_user_profile()
        print("✅ User profile test passed")
        
        test_instance.setup_method()
        test_instance.test_unauthorized_access()
        print("✅ Unauthorized access test passed")
        
        test_instance.setup_method()
        test_instance.test_team_creation()
        print("✅ Team creation test passed")
        
        test_instance.setup_method()
        test_instance.test_settings_sync()
        print("✅ Settings sync test passed")
        
        test_instance.setup_method()
        test_instance.test_bookmarks()
        print("✅ Bookmarks test passed")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
