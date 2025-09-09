import pytest
import io
from fastapi.testclient import TestClient


class TestUploads:
    """Test upload endpoints."""

    def test_get_presigned_url_unauthorized(self, client):
        """Test getting presigned URL without authentication."""
        request_data = {
            "file_name": "test.jpg",
            "file_type": "image/jpeg",
            "file_size": 1024
        }
        response = client.post("/uploads/presigned-url", json=request_data)
        assert response.status_code == 401

    def test_get_presigned_url_success(self, client, authenticated_user_token):
        """Test successful presigned URL generation."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        request_data = {
            "file_name": "test.jpg",
            "file_type": "image/jpeg",
            "file_size": 1024
        }
        
        response = client.post("/uploads/presigned-url", json=request_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "upload_url" in data
        assert "file_id" in data
        assert "expires_in" in data
        
        # Check data types and values
        assert isinstance(data["upload_url"], str)
        assert isinstance(data["file_id"], str)
        assert isinstance(data["expires_in"], int)
        assert data["expires_in"] == 3600
        assert len(data["file_id"]) > 0

    def test_get_presigned_url_invalid_file_type(self, client, authenticated_user_token):
        """Test presigned URL generation with invalid file type."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        request_data = {
            "file_name": "test.exe",
            "file_type": "application/x-executable",
            "file_size": 1024
        }
        
        response = client.post("/uploads/presigned-url", json=request_data, headers=headers)
        
        assert response.status_code == 400
        assert "File type not allowed" in response.json()["detail"]

    def test_get_presigned_url_file_too_large(self, client, authenticated_user_token):
        """Test presigned URL generation with file too large."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        request_data = {
            "file_name": "large_file.jpg",
            "file_type": "image/jpeg",
            "file_size": 20 * 1024 * 1024  # 20MB, larger than 10MB limit
        }
        
        response = client.post("/uploads/presigned-url", json=request_data, headers=headers)
        
        assert response.status_code == 400
        assert "File size too large" in response.json()["detail"]

    def test_get_presigned_url_missing_fields(self, client, authenticated_user_token):
        """Test presigned URL generation with missing required fields."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Test without file_name
        request_data = {
            "file_type": "image/jpeg",
            "file_size": 1024
        }
        response = client.post("/uploads/presigned-url", json=request_data, headers=headers)
        assert response.status_code == 422  # Validation error
        
        # Test without file_type
        request_data = {
            "file_name": "test.jpg",
            "file_size": 1024
        }
        response = client.post("/uploads/presigned-url", json=request_data, headers=headers)
        assert response.status_code == 422  # Validation error
        
        # Test without file_size
        request_data = {
            "file_name": "test.jpg",
            "file_type": "image/jpeg"
        }
        response = client.post("/uploads/presigned-url", json=request_data, headers=headers)
        assert response.status_code == 422  # Validation error

    def test_upload_file_unauthorized(self, client):
        """Test file upload without authentication."""
        file_content = b"test file content"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        
        response = client.post("/uploads/", files=files)
        assert response.status_code == 401

    def test_upload_file_success(self, client, authenticated_user_token):
        """Test successful file upload."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        file_content = b"test file content"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        
        response = client.post("/uploads/", files=files, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "file_id" in data
        assert "url" in data
        assert "file_name" in data
        assert "file_size" in data
        assert "file_type" in data
        
        # Check data values
        assert isinstance(data["file_id"], str)
        assert isinstance(data["url"], str)
        assert data["file_name"] == "test.txt"
        assert data["file_size"] == len(file_content)
        assert data["file_type"] == "text/plain"

    def test_upload_file_invalid_type(self, client, authenticated_user_token):
        """Test file upload with invalid file type."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        file_content = b"executable content"
        files = {"file": ("test.exe", io.BytesIO(file_content), "application/x-executable")}
        
        response = client.post("/uploads/", files=files, headers=headers)
        
        assert response.status_code == 400
        assert "File type not allowed" in response.json()["detail"]

    def test_upload_file_too_large(self, client, authenticated_user_token):
        """Test file upload with file too large."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        # Create a large file content (11MB)
        large_content = b"x" * (11 * 1024 * 1024)
        files = {"file": ("large.txt", io.BytesIO(large_content), "text/plain")}
        
        response = client.post("/uploads/", files=files, headers=headers)
        
        assert response.status_code == 400
        assert "File size too large" in response.json()["detail"]

    def test_upload_file_no_file(self, client, authenticated_user_token):
        """Test file upload without file."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        response = client.post("/uploads/", headers=headers)
        assert response.status_code == 422  # Validation error

    def test_upload_file_empty_filename(self, client, authenticated_user_token):
        """Test file upload with empty filename."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        file_content = b"test content"
        files = {"file": ("", io.BytesIO(file_content), "text/plain")}
        
        response = client.post("/uploads/", files=files, headers=headers)
        
        # FastAPI returns 422 for empty filename before our custom validation
        assert response.status_code == 422

    def test_get_file_success(self, client):
        """Test getting uploaded file."""
        file_id = "test-file-id"
        response = client.get(f"/uploads/{file_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure (mock response)
        assert "message" in data
        assert "file_id" in data
        assert data["file_id"] == file_id

    def test_upload_workflow(self, client, authenticated_user_token):
        """Test complete upload workflow."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # 1. Get presigned URL
        presigned_request = {
            "file_name": "workflow_test.jpg",
            "file_type": "image/jpeg",
            "file_size": 2048
        }
        presigned_response = client.post("/uploads/presigned-url", json=presigned_request, headers=headers)
        assert presigned_response.status_code == 200
        presigned_data = presigned_response.json()
        
        # 2. Upload file directly
        file_content = b"test image content"
        files = {"file": ("workflow_test.jpg", io.BytesIO(file_content), "image/jpeg")}
        upload_response = client.post("/uploads/", files=files, headers=headers)
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        
        # 3. Get uploaded file
        file_id = upload_data["file_id"]
        get_response = client.get(f"/uploads/{file_id}")
        assert get_response.status_code == 200
        
        # Check that file IDs are different (presigned vs direct upload)
        assert presigned_data["file_id"] != upload_data["file_id"]

    def test_upload_different_file_types(self, client, authenticated_user_token):
        """Test uploading different allowed file types."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        allowed_files = [
            ("test.jpg", "image/jpeg"),
            ("test.png", "image/png"),
            ("test.gif", "image/gif"),
            ("test.pdf", "application/pdf"),
            ("test.doc", "application/msword"),
        ]
        
        for filename, content_type in allowed_files:
            file_content = b"test content"
            files = {"file": (filename, io.BytesIO(file_content), content_type)}
            
            response = client.post("/uploads/", files=files, headers=headers)
            assert response.status_code == 200
            
            data = response.json()
            assert data["file_name"] == filename
            assert data["file_type"] == content_type

    def test_upload_response_format(self, client, authenticated_user_token):
        """Test that upload responses have correct format."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Test presigned URL response format
        presigned_request = {
            "file_name": "format_test.jpg",
            "file_type": "image/jpeg",
            "file_size": 1024
        }
        presigned_response = client.post("/uploads/presigned-url", json=presigned_request, headers=headers)
        assert presigned_response.status_code == 200
        presigned_data = presigned_response.json()
        
        required_presigned_fields = ["upload_url", "file_id", "expires_in"]
        for field in required_presigned_fields:
            assert field in presigned_data, f"Missing required field: {field}"
        
        # Test direct upload response format
        file_content = b"test content"
        files = {"file": ("format_test.txt", io.BytesIO(file_content), "text/plain")}
        upload_response = client.post("/uploads/", files=files, headers=headers)
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        
        required_upload_fields = ["file_id", "url", "file_name", "file_size", "file_type"]
        for field in required_upload_fields:
            assert field in upload_data, f"Missing required field: {field}"
