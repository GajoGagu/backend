import pytest
from fastapi.testclient import TestClient


class TestUserAuth:
    """Test user authentication endpoints."""

    def test_user_signup_success(self, client, sample_user_data):
        """Test successful user signup."""
        response = client.post("/auth/users/signup", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Check response structure
        assert "user" in data
        assert "tokens" in data
        
        # Check user data
        user = data["user"]
        assert user["email"] == sample_user_data["email"]
        assert user["name"] == sample_user_data["name"]
        assert user["phone"] == sample_user_data["phone"]
        assert user["role"] == "user"
        assert "id" in user
        assert "created_at" in user
        
        # Check tokens
        tokens = data["tokens"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert len(tokens["access_token"]) > 0
        assert len(tokens["refresh_token"]) > 0

    def test_user_signup_duplicate_email(self, client, sample_user_data):
        """Test user signup with duplicate email."""
        # First signup
        response1 = client.post("/auth/users/signup", json=sample_user_data)
        assert response1.status_code == 201
        
        # Second signup with same email
        response2 = client.post("/auth/users/signup", json=sample_user_data)
        assert response2.status_code == 400
        assert "Email already exists" in response2.json()["detail"]

    def test_user_signup_invalid_data(self, client):
        """Test user signup with invalid data."""
        invalid_data = {
            "email": "invalid-email",
            "password": "123",  # Too short
            "name": "",
            "phone": "invalid-phone"
        }
        
        response = client.post("/auth/users/signup", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_user_login_success(self, client, sample_user_data):
        """Test successful user login."""
        # First signup
        signup_response = client.post("/auth/users/signup", json=sample_user_data)
        assert signup_response.status_code == 201
        
        # Then login
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        response = client.post("/auth/users/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "user" in data
        assert "tokens" in data
        
        # Check user data
        user = data["user"]
        assert user["email"] == sample_user_data["email"]
        assert user["role"] == "user"

    def test_user_login_invalid_credentials(self, client, sample_user_data):
        """Test user login with invalid credentials."""
        # Try to login without signing up
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        response = client.post("/auth/users/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_user_login_wrong_password(self, client, sample_user_data):
        """Test user login with wrong password."""
        # First signup
        signup_response = client.post("/auth/users/signup", json=sample_user_data)
        assert signup_response.status_code == 201
        
        # Then login with wrong password
        login_data = {
            "email": sample_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/auth/users/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]


class TestRiderAuth:
    """Test rider authentication endpoints."""

    def test_rider_signup_success(self, client, sample_rider_data):
        """Test successful rider signup."""
        response = client.post("/auth/riders/signup", json=sample_rider_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Check response structure
        assert "user" in data
        assert "tokens" in data
        
        # Check rider data
        rider = data["user"]
        assert rider["email"] == sample_rider_data["email"]
        assert rider["name"] == sample_rider_data["name"]
        assert rider["phone"] == sample_rider_data["phone"]
        assert rider["role"] == "rider"
        assert "id" in rider
        assert "created_at" in rider
        assert "vehicle_type" in rider
        assert "rating" in rider

    def test_rider_signup_duplicate_email(self, client, sample_rider_data):
        """Test rider signup with duplicate email."""
        # First signup
        response1 = client.post("/auth/riders/signup", json=sample_rider_data)
        assert response1.status_code == 201
        
        # Second signup with same email
        response2 = client.post("/auth/riders/signup", json=sample_rider_data)
        assert response2.status_code == 400
        assert "Email already exists" in response2.json()["detail"]

    def test_rider_login_success(self, client, sample_rider_data):
        """Test successful rider login."""
        # First signup
        signup_response = client.post("/auth/riders/signup", json=sample_rider_data)
        assert signup_response.status_code == 201
        
        # Then login
        login_data = {
            "email": sample_rider_data["email"],
            "password": sample_rider_data["password"]
        }
        response = client.post("/auth/riders/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "user" in data
        assert "tokens" in data
        
        # Check rider data
        rider = data["user"]
        assert rider["email"] == sample_rider_data["email"]
        assert rider["role"] == "rider"

    def test_rider_login_invalid_credentials(self, client, sample_rider_data):
        """Test rider login with invalid credentials."""
        # Try to login without signing up
        login_data = {
            "email": sample_rider_data["email"],
            "password": sample_rider_data["password"]
        }
        response = client.post("/auth/riders/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]


class TestAuthIntegration:
    """Test authentication integration scenarios."""

    def test_user_and_rider_separate_databases(self, client, sample_user_data, sample_rider_data):
        """Test that users and riders are stored in separate databases."""
        # Sign up user
        user_response = client.post("/auth/users/signup", json=sample_user_data)
        assert user_response.status_code == 201
        
        # Sign up rider with same email (should be allowed)
        rider_response = client.post("/auth/riders/signup", json=sample_rider_data)
        assert rider_response.status_code == 201
        
        # Both should be able to login
        user_login = client.post("/auth/users/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        assert user_login.status_code == 200
        
        rider_login = client.post("/auth/riders/login", json={
            "email": sample_rider_data["email"],
            "password": sample_rider_data["password"]
        })
        assert rider_login.status_code == 200

    def test_token_generation_uniqueness(self, client, sample_user_data):
        """Test that tokens are unique for each login."""
        # Sign up user
        signup_response = client.post("/auth/users/signup", json=sample_user_data)
        assert signup_response.status_code == 201
        signup_token = signup_response.json()["tokens"]["access_token"]
        
        # Login user
        login_response = client.post("/auth/users/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        assert login_response.status_code == 200
        login_token = login_response.json()["tokens"]["access_token"]
        
        # Tokens should be different
        assert signup_token != login_token
