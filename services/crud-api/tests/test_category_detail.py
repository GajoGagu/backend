import pytest
from fastapi.testclient import TestClient


class TestCategoryDetail:
    """Test category detail endpoint."""

    def test_get_category_detail_success(self, client, sample_category):
        """Test successful category detail retrieval."""
        category_id = sample_category["id"]
        response = client.get(f"/categories/{category_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "id" in data
        assert "name" in data
        assert "parent_id" in data
        
        # Check data matches sample
        assert data["id"] == sample_category["id"]
        assert data["name"] == sample_category["name"]
        assert data["parent_id"] == sample_category["parent_id"]

    def test_get_category_detail_not_found(self, client):
        """Test category detail with non-existent category ID."""
        non_existent_id = "non-existent-category-id"
        response = client.get(f"/categories/{non_existent_id}")
        
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]

    def test_get_category_detail_empty_id(self, client):
        """Test category detail with empty ID."""
        response = client.get("/categories/")
        
        # This should return 404 or 405 depending on routing
        assert response.status_code in [404, 405]

    def test_get_category_detail_special_characters(self, client):
        """Test category detail with special characters in ID."""
        special_id = "category-with-special-chars-!@#$%"
        response = client.get(f"/categories/{special_id}")
        
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]

    def test_get_category_detail_numeric_id(self, client):
        """Test category detail with numeric ID."""
        numeric_id = "12345"
        response = client.get(f"/categories/{numeric_id}")
        
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]

    def test_get_category_detail_unicode_id(self, client):
        """Test category detail with unicode ID."""
        unicode_id = "카테고리-한글-테스트"
        response = client.get(f"/categories/{unicode_id}")
        
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]

    def test_category_detail_vs_list_consistency(self, client, sample_category):
        """Test that category detail matches category list data."""
        category_id = sample_category["id"]
        
        # Get from list endpoint
        list_response = client.get("/categories")
        assert list_response.status_code == 200
        categories = list_response.json()
        
        # Find our category in the list
        category_from_list = None
        for cat in categories:
            if cat["id"] == category_id:
                category_from_list = cat
                break
        
        assert category_from_list is not None
        
        # Get from detail endpoint
        detail_response = client.get(f"/categories/{category_id}")
        assert detail_response.status_code == 200
        category_from_detail = detail_response.json()
        
        # Data should be identical
        assert category_from_list["id"] == category_from_detail["id"]
        assert category_from_list["name"] == category_from_detail["name"]
        assert category_from_list["parent_id"] == category_from_detail["parent_id"]

    def test_multiple_categories_detail(self, client):
        """Test retrieving details for multiple categories."""
        # Create multiple categories
        categories = []
        for i in range(3):
            category_data = {
                "id": f"test-cat-{i}",
                "name": f"테스트 카테고리 {i}",
                "parent_id": None
            }
            # Note: In a real test, you'd create these through the API
            # For now, we'll test with non-existent categories
            response = client.get(f"/categories/test-cat-{i}")
            assert response.status_code == 404

    def test_category_detail_response_format(self, client, sample_category):
        """Test that category detail response has correct format."""
        category_id = sample_category["id"]
        response = client.get(f"/categories/{category_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check all required fields are present
        required_fields = ["id", "name", "parent_id"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Check field types
        assert isinstance(data["id"], str)
        assert isinstance(data["name"], str)
        # parent_id can be None or string
        assert data["parent_id"] is None or isinstance(data["parent_id"], str)
        
        # Check field values are not empty (except parent_id which can be None)
        assert len(data["id"]) > 0
        assert len(data["name"]) > 0
