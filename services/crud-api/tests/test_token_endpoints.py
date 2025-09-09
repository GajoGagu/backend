import pytest
from fastapi.testclient import TestClient


class TestTokenEndpoints:
    """Test token-related endpoints (refresh, logout)."""

    def test_refresh_token_success(self, client, sample_user_data):
        """Test successful token refresh."""
        # Sign up user
        signup_response = client.post("/auth/users/signup", json=sample_user_data)
        assert signup_response.status_code == 201
        refresh_token = signup_response.json()["tokens"]["refresh_token"]
        
        # Refresh token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/auth/users/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "user" in data
        assert "tokens" in data
        
        # Check that new tokens are generated
        new_tokens = data["tokens"]
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        assert len(new_tokens["access_token"]) > 0
        assert len(new_tokens["refresh_token"]) > 0
        
        # New tokens should be different from original
        assert new_tokens["access_token"] != signup_response.json()["tokens"]["access_token"]
        assert new_tokens["refresh_token"] != refresh_token

    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token."""
        refresh_data = {"refresh_token": "invalid_token"}
        response = client.post("/auth/users/refresh", json=refresh_data)
        
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]

    def test_refresh_token_empty(self, client):
        """Test refresh with empty token."""
        refresh_data = {"refresh_token": ""}
        response = client.post("/auth/users/refresh", json=refresh_data)
        
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]

    def test_logout_success(self, client, sample_user_data):
        """Test successful logout."""
        # Sign up user
        signup_response = client.post("/auth/users/signup", json=sample_user_data)
        assert signup_response.status_code == 201
        access_token = signup_response.json()["tokens"]["access_token"]
        
        # Logout
        logout_data = {"access_token": access_token}
        response = client.post("/auth/users/logout", json=logout_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Successfully logged out" in data["message"]

    def test_logout_invalid_token(self, client):
        """Test logout with invalid token."""
        logout_data = {"access_token": "invalid_token"}
        response = client.post("/auth/users/logout", json=logout_data)
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_logout_empty_token(self, client):
        """Test logout with empty token."""
        logout_data = {"access_token": ""}
        response = client.post("/auth/users/logout", json=logout_data)
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_logout_nonexistent_token(self, client):
        """Test logout with non-existent token."""
        logout_data = {"access_token": "nonexistent_token_12345"}
        response = client.post("/auth/users/logout", json=logout_data)
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_token_workflow(self, client, sample_user_data):
        """Test complete token workflow: signup -> login -> refresh -> logout."""
        # 1. Sign up
        signup_response = client.post("/auth/users/signup", json=sample_user_data)
        assert signup_response.status_code == 201
        original_tokens = signup_response.json()["tokens"]
        
        # 2. Login
        login_response = client.post("/auth/users/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        assert login_response.status_code == 200
        login_tokens = login_response.json()["tokens"]
        
        # 3. Refresh token
        refresh_response = client.post("/auth/users/refresh", json={
            "refresh_token": login_tokens["refresh_token"]
        })
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()["tokens"]
        
        # 4. Logout with new access token
        logout_response = client.post("/auth/users/logout", json={
            "access_token": new_tokens["access_token"]
        })
        assert logout_response.status_code == 200
        
        # 5. Try to use the logged out token (should fail)
        # This would require a protected endpoint to test properly
        # For now, we just verify the logout was successful
        assert "Successfully logged out" in logout_response.json()["message"]

    def test_multiple_refresh_tokens(self, client, sample_user_data):
        """Test that multiple refresh operations work correctly."""
        # Sign up user
        signup_response = client.post("/auth/users/signup", json=sample_user_data)
        assert signup_response.status_code == 201
        refresh_token = signup_response.json()["tokens"]["refresh_token"]
        
        # First refresh
        refresh1_response = client.post("/auth/users/refresh", json={
            "refresh_token": refresh_token
        })
        assert refresh1_response.status_code == 200
        new_refresh_token = refresh1_response.json()["tokens"]["refresh_token"]
        
        # Second refresh with new refresh token
        refresh2_response = client.post("/auth/users/refresh", json={
            "refresh_token": new_refresh_token
        })
        assert refresh2_response.status_code == 200
        
        # All tokens should be different
        original_access = signup_response.json()["tokens"]["access_token"]
        first_access = refresh1_response.json()["tokens"]["access_token"]
        second_access = refresh2_response.json()["tokens"]["access_token"]
        
        assert original_access != first_access
        assert first_access != second_access
        assert original_access != second_access
