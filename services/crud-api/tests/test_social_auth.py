import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient


class TestSocialAuth:
    """Test social authentication endpoints."""

    def test_google_login_unauthorized(self, client):
        """Test Google login without proper token."""
        request_data = {
            "access_token": "invalid_google_token",
            "provider": "google"
        }
        response = client.post("/auth/social/google", json=request_data)
        assert response.status_code == 401
        assert "Invalid Google token" in response.json()["detail"]

    @patch('routers.auth.verify_social_token')
    def test_google_login_success(self, mock_verify, client):
        """Test successful Google login."""
        # Mock successful token verification
        mock_verify.return_value = {
            "id": "google_user_123",
            "email": "user@gmail.com",
            "name": "Google User",
            "picture": "https://example.com/avatar.jpg"
        }
        
        request_data = {
            "access_token": "valid_google_token",
            "provider": "google"
        }
        response = client.post("/auth/social/google", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "user" in data
        assert "tokens" in data
        
        # Check user data
        user = data["user"]
        assert user["email"] == "user@gmail.com"
        assert user["name"] == "Google User"
        assert user["role"] == "user"
        assert "id" in user
        assert "created_at" in user
        
        # Check tokens
        tokens = data["tokens"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert len(tokens["access_token"]) > 0
        assert len(tokens["refresh_token"]) > 0

    @patch('routers.auth.verify_social_token')
    def test_google_login_existing_user(self, mock_verify, client, sample_user_data):
        """Test Google login with existing user email."""
        # First create a regular user
        signup_response = client.post("/auth/users/signup", json=sample_user_data)
        assert signup_response.status_code == 201
        
        # Mock successful token verification with same email
        mock_verify.return_value = {
            "id": "google_user_456",
            "email": sample_user_data["email"],  # Same email as existing user
            "name": "Google User",
            "picture": "https://example.com/avatar.jpg"
        }
        
        request_data = {
            "access_token": "valid_google_token",
            "provider": "google"
        }
        response = client.post("/auth/social/google", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return existing user data
        user = data["user"]
        assert user["email"] == sample_user_data["email"]
        assert user["name"] == sample_user_data["name"]  # Should use existing name

    def test_google_login_missing_fields(self, client):
        """Test Google login with missing required fields."""
        # Test without access_token
        request_data = {"provider": "google"}
        response = client.post("/auth/social/google", json=request_data)
        assert response.status_code == 422  # Validation error
        
        # Test without provider
        request_data = {"access_token": "some_token"}
        response = client.post("/auth/social/google", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_kakao_login_unauthorized(self, client):
        """Test Kakao login without proper token."""
        request_data = {
            "access_token": "invalid_kakao_token",
            "provider": "kakao"
        }
        response = client.post("/auth/social/kakao", json=request_data)
        assert response.status_code == 401
        assert "Invalid Kakao token" in response.json()["detail"]

    @patch('routers.auth.verify_social_token')
    def test_kakao_login_success(self, mock_verify, client):
        """Test successful Kakao login."""
        # Mock successful token verification
        mock_verify.return_value = {
            "id": "kakao_user_123",
            "email": "user@kakao.com",
            "name": "Kakao User",
            "picture": "https://example.com/kakao_avatar.jpg"
        }
        
        request_data = {
            "access_token": "valid_kakao_token",
            "provider": "kakao"
        }
        response = client.post("/auth/social/kakao", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "user" in data
        assert "tokens" in data
        
        # Check user data
        user = data["user"]
        assert user["email"] == "user@kakao.com"
        assert user["name"] == "Kakao User"
        assert user["role"] == "user"
        assert "id" in user
        assert "created_at" in user
        
        # Check tokens
        tokens = data["tokens"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert len(tokens["access_token"]) > 0
        assert len(tokens["refresh_token"]) > 0

    @patch('routers.auth.verify_social_token')
    def test_kakao_login_existing_user(self, mock_verify, client, sample_user_data):
        """Test Kakao login with existing user email."""
        # First create a regular user
        signup_response = client.post("/auth/users/signup", json=sample_user_data)
        assert signup_response.status_code == 201
        
        # Mock successful token verification with same email
        mock_verify.return_value = {
            "id": "kakao_user_456",
            "email": sample_user_data["email"],  # Same email as existing user
            "name": "Kakao User",
            "picture": "https://example.com/kakao_avatar.jpg"
        }
        
        request_data = {
            "access_token": "valid_kakao_token",
            "provider": "kakao"
        }
        response = client.post("/auth/social/kakao", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return existing user data
        user = data["user"]
        assert user["email"] == sample_user_data["email"]
        assert user["name"] == sample_user_data["name"]  # Should use existing name

    def test_kakao_login_missing_fields(self, client):
        """Test Kakao login with missing required fields."""
        # Test without access_token
        request_data = {"provider": "kakao"}
        response = client.post("/auth/social/kakao", json=request_data)
        assert response.status_code == 422  # Validation error
        
        # Test without provider
        request_data = {"access_token": "some_token"}
        response = client.post("/auth/social/kakao", json=request_data)
        assert response.status_code == 422  # Validation error

    @patch('routers.auth.verify_social_token')
    def test_social_login_without_name(self, mock_verify, client):
        """Test social login when user doesn't provide name."""
        # Mock token verification without name
        mock_verify.return_value = {
            "id": "social_user_123",
            "email": "user@example.com",
            "name": None,
            "picture": None
        }
        
        request_data = {
            "access_token": "valid_token",
            "provider": "google"
        }
        response = client.post("/auth/social/google", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        user = data["user"]
        assert user["email"] == "user@example.com"
        # Name should be derived from email if not provided
        assert user["name"] == "user"  # email.split("@")[0]

    @patch('routers.auth.verify_social_token')
    def test_social_login_token_verification_failure(self, mock_verify, client):
        """Test social login when token verification fails."""
        # Mock failed token verification
        mock_verify.return_value = None
        
        request_data = {
            "access_token": "invalid_token",
            "provider": "google"
        }
        response = client.post("/auth/social/google", json=request_data)
        
        assert response.status_code == 401
        assert "Invalid Google token" in response.json()["detail"]

    @patch('routers.auth.verify_social_token')
    def test_social_login_workflow(self, mock_verify, client):
        """Test complete social login workflow."""
        # Mock successful token verification
        mock_verify.return_value = {
            "id": "workflow_user_123",
            "email": "workflow@example.com",
            "name": "Workflow User",
            "picture": "https://example.com/avatar.jpg"
        }
        
        # 1. Google login
        google_request = {
            "access_token": "google_token",
            "provider": "google"
        }
        google_response = client.post("/auth/social/google", json=google_request)
        assert google_response.status_code == 200
        google_data = google_response.json()
        
        # 2. Kakao login (different user)
        mock_verify.return_value = {
            "id": "workflow_user_456",
            "email": "workflow2@example.com",
            "name": "Workflow User 2",
            "picture": "https://example.com/avatar2.jpg"
        }
        
        kakao_request = {
            "access_token": "kakao_token",
            "provider": "kakao"
        }
        kakao_response = client.post("/auth/social/kakao", json=kakao_request)
        assert kakao_response.status_code == 200
        kakao_data = kakao_response.json()
        
        # Both should have different user IDs and tokens
        assert google_data["user"]["id"] != kakao_data["user"]["id"]
        assert google_data["tokens"]["access_token"] != kakao_data["tokens"]["access_token"]

    def test_social_login_response_format(self, client):
        """Test that social login responses have correct format."""
        # Test with invalid token to check error format
        request_data = {
            "access_token": "invalid_token",
            "provider": "google"
        }
        response = client.post("/auth/social/google", json=request_data)
        
        assert response.status_code == 401
        error_data = response.json()
        assert "detail" in error_data
        assert isinstance(error_data["detail"], str)

    def test_social_login_provider_validation(self, client):
        """Test social login with different provider values."""
        # Test with unsupported provider
        request_data = {
            "access_token": "some_token",
            "provider": "facebook"  # Not supported
        }
        response = client.post("/auth/social/google", json=request_data)
        
        # Should still process the request (provider is just for reference)
        assert response.status_code == 401  # Invalid token, not provider error

    @patch('routers.auth.verify_social_token')
    def test_social_login_token_uniqueness(self, mock_verify, client):
        """Test that social login generates unique tokens."""
        # Mock successful token verification
        mock_verify.return_value = {
            "id": "unique_user_123",
            "email": "unique@example.com",
            "name": "Unique User",
            "picture": None
        }
        
        # First login
        request_data = {
            "access_token": "token1",
            "provider": "google"
        }
        response1 = client.post("/auth/social/google", json=request_data)
        assert response1.status_code == 200
        tokens1 = response1.json()["tokens"]
        
        # Second login with different token
        request_data = {
            "access_token": "token2",
            "provider": "google"
        }
        response2 = client.post("/auth/social/google", json=request_data)
        assert response2.status_code == 200
        tokens2 = response2.json()["tokens"]
        
        # Tokens should be different
        assert tokens1["access_token"] != tokens2["access_token"]
        assert tokens1["refresh_token"] != tokens2["refresh_token"]
