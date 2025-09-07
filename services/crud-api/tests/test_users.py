import pytest
from fastapi.testclient import TestClient


class TestUserProfile:
    """Test user profile endpoints."""

    def test_get_user_profile_success(self, client, authenticated_user_token, sample_user_data):
        """Test successful user profile retrieval."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        response = client.get("/users/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check user data
        assert data["email"] == sample_user_data["email"]
        assert data["name"] == sample_user_data["name"]
        assert data["phone"] == sample_user_data["phone"]
        assert data["role"] == "user"
        assert "id" in data
        assert "created_at" in data

    def test_get_user_profile_unauthorized(self, client):
        """Test user profile retrieval without authentication."""
        response = client.get("/users/me")
        assert response.status_code == 401

    def test_user_profile_data_consistency(self, client, sample_user_data):
        """Test that user profile data is consistent with signup data."""
        # Sign up user
        signup_response = client.post("/auth/users/signup", json=sample_user_data)
        assert signup_response.status_code == 201
        signup_user = signup_response.json()["user"]
        token = signup_response.json()["tokens"]["access_token"]
        
        # Get profile
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = client.get("/users/me", headers=headers)
        assert profile_response.status_code == 200
        profile_user = profile_response.json()
        
        # Compare data
        assert profile_user["id"] == signup_user["id"]
        assert profile_user["email"] == signup_user["email"]
        assert profile_user["name"] == signup_user["name"]
        assert profile_user["phone"] == signup_user["phone"]
        assert profile_user["role"] == signup_user["role"]
        assert profile_user["created_at"] == signup_user["created_at"]

    def test_rider_profile_data(self, client, sample_rider_data):
        """Test rider profile data structure."""
        # Sign up rider
        signup_response = client.post("/auth/riders/signup", json=sample_rider_data)
        assert signup_response.status_code == 201
        signup_rider = signup_response.json()["user"]
        token = signup_response.json()["tokens"]["access_token"]
        
        # Get profile
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = client.get("/users/me", headers=headers)
        assert profile_response.status_code == 200
        profile_rider = profile_response.json()
        
        # Check rider-specific fields
        assert profile_rider["role"] == "rider"
        assert "vehicle_type" in profile_rider
        assert "rating" in profile_rider
        assert profile_rider["vehicle_type"] == "car"
        assert profile_rider["rating"] == 0.0

    def test_user_profile_after_login(self, client, sample_user_data):
        """Test user profile after login."""
        # Sign up user
        signup_response = client.post("/auth/users/signup", json=sample_user_data)
        assert signup_response.status_code == 201
        
        # Login user
        login_response = client.post("/auth/users/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        assert login_response.status_code == 200
        token = login_response.json()["tokens"]["access_token"]
        
        # Get profile with login token
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = client.get("/users/me", headers=headers)
        assert profile_response.status_code == 200
        profile_user = profile_response.json()
        
        # Verify profile data
        assert profile_user["email"] == sample_user_data["email"]
        assert profile_user["name"] == sample_user_data["name"]
        assert profile_user["role"] == "user"
