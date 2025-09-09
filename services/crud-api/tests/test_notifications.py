import pytest
from fastapi.testclient import TestClient


class TestNotifications:
    """Test notification endpoints."""

    def test_get_notifications_unauthorized(self, client):
        """Test getting notifications without authentication."""
        response = client.get("/notifications")
        assert response.status_code == 401

    def test_get_notifications_success(self, client, authenticated_user_token):
        """Test successful notification retrieval."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        response = client.get("/notifications", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "notifications" in data
        assert "total" in data
        assert "unread_count" in data
        
        # Check data types
        assert isinstance(data["notifications"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["unread_count"], int)
        
        # Initially should have no notifications
        assert data["total"] == 0
        assert data["unread_count"] == 0

    def test_get_notifications_with_pagination(self, client, authenticated_user_token):
        """Test notification retrieval with pagination parameters."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Test with pagination parameters
        response = client.get("/notifications?skip=0&limit=10", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "notifications" in data
        assert "total" in data
        assert "unread_count" in data

    def test_get_notifications_invalid_pagination(self, client, authenticated_user_token):
        """Test notification retrieval with invalid pagination parameters."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Test with negative skip
        response = client.get("/notifications?skip=-1", headers=headers)
        assert response.status_code == 422  # Validation error
        
        # Test with zero limit
        response = client.get("/notifications?limit=0", headers=headers)
        assert response.status_code == 422  # Validation error
        
        # Test with too large limit
        response = client.get("/notifications?limit=1000", headers=headers)
        assert response.status_code == 422  # Validation error

    def test_mark_notifications_as_read_unauthorized(self, client):
        """Test marking notifications as read without authentication."""
        request_data = {"notification_ids": ["test-id"]}
        response = client.post("/notifications/mark-as-read", json=request_data)
        assert response.status_code == 401

    def test_mark_notifications_as_read_success(self, client, authenticated_user_token):
        """Test successful marking of notifications as read."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        request_data = {"notification_ids": ["test-id-1", "test-id-2"]}
        
        response = client.post("/notifications/mark-as-read", json=request_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "message" in data
        assert "updated_count" in data
        
        # Should return 0 since no notifications exist
        assert data["updated_count"] == 0
        assert "Marked 0 notifications as read" in data["message"]

    def test_mark_notifications_as_read_empty_list(self, client, authenticated_user_token):
        """Test marking notifications as read with empty list."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        request_data = {"notification_ids": []}
        
        response = client.post("/notifications/mark-as-read", json=request_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated_count"] == 0

    def test_mark_notifications_as_read_invalid_data(self, client, authenticated_user_token):
        """Test marking notifications as read with invalid data."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Test without notification_ids
        response = client.post("/notifications/mark-as-read", json={}, headers=headers)
        assert response.status_code == 422  # Validation error
        
        # Test with invalid notification_ids type
        response = client.post("/notifications/mark-as-read", json={"notification_ids": "not-a-list"}, headers=headers)
        assert response.status_code == 422  # Validation error

    def test_get_unread_count_unauthorized(self, client):
        """Test getting unread count without authentication."""
        response = client.get("/notifications/unread-count")
        assert response.status_code == 401

    def test_get_unread_count_success(self, client, authenticated_user_token):
        """Test successful unread count retrieval."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        response = client.get("/notifications/unread-count", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "unread_count" in data
        assert isinstance(data["unread_count"], int)
        
        # Initially should have 0 unread notifications
        assert data["unread_count"] == 0

    def test_notification_endpoints_consistency(self, client, authenticated_user_token):
        """Test that notification endpoints return consistent data."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Get notifications list
        list_response = client.get("/notifications", headers=headers)
        assert list_response.status_code == 200
        list_data = list_response.json()
        
        # Get unread count
        count_response = client.get("/notifications/unread-count", headers=headers)
        assert count_response.status_code == 200
        count_data = count_response.json()
        
        # Unread count should match
        assert list_data["unread_count"] == count_data["unread_count"]

    def test_notification_workflow(self, client, authenticated_user_token):
        """Test complete notification workflow."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # 1. Get initial notifications (should be empty)
        response = client.get("/notifications", headers=headers)
        assert response.status_code == 200
        initial_data = response.json()
        assert initial_data["total"] == 0
        assert initial_data["unread_count"] == 0
        
        # 2. Get unread count (should be 0)
        count_response = client.get("/notifications/unread-count", headers=headers)
        assert count_response.status_code == 200
        assert count_response.json()["unread_count"] == 0
        
        # 3. Try to mark non-existent notifications as read
        mark_response = client.post("/notifications/mark-as-read", 
                                  json={"notification_ids": ["non-existent"]}, 
                                  headers=headers)
        assert mark_response.status_code == 200
        assert mark_response.json()["updated_count"] == 0

    def test_notification_headers_required(self, client):
        """Test that proper authorization headers are required."""
        # Test without Authorization header
        response = client.get("/notifications")
        assert response.status_code == 401
        
        # Test with invalid Authorization header
        response = client.get("/notifications", headers={"Authorization": "Invalid token"})
        assert response.status_code == 401
        
        # Test with malformed Authorization header
        response = client.get("/notifications", headers={"Authorization": "Bearer"})
        assert response.status_code == 401

    def test_notification_response_format(self, client, authenticated_user_token):
        """Test that notification responses have correct format."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Test notifications list response format
        response = client.get("/notifications", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = ["notifications", "total", "unread_count"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Check data types
        assert isinstance(data["notifications"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["unread_count"], int)
        
        # Check unread count response format
        count_response = client.get("/notifications/unread-count", headers=headers)
        assert count_response.status_code == 200
        count_data = count_response.json()
        
        assert "unread_count" in count_data
        assert isinstance(count_data["unread_count"], int)
