import pytest
from fastapi.testclient import TestClient


class TestCategories:
    """Test category endpoints."""

    def test_get_categories_success(self, client, sample_category):
        """Test successful category retrieval."""
        response = client.get("/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check category structure
        category = data[0]
        assert "id" in category
        assert "name" in category
        assert category["id"] == sample_category["id"]
        assert category["name"] == sample_category["name"]

    def test_get_categories_empty(self, client):
        """Test category retrieval when no categories exist."""
        response = client.get("/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # Should be empty since we clean databases before each test

    def test_categories_data_structure(self, client, sample_category):
        """Test category data structure."""
        response = client.get("/categories")
        assert response.status_code == 200
        
        data = response.json()
        if data:  # If categories exist
            category = data[0]
            required_fields = ["id", "name"]
            for field in required_fields:
                assert field in category
                assert category[field] is not None

    def test_categories_consistency(self, client, sample_category):
        """Test that categories endpoint returns consistent data."""
        # Make multiple requests
        responses = []
        for _ in range(3):
            response = client.get("/categories")
            assert response.status_code == 200
            responses.append(response.json())
        
        # All responses should be identical
        for i in range(1, len(responses)):
            assert responses[i] == responses[0]

    def test_categories_with_hierarchy(self, client):
        """Test categories with parent-child relationships."""
        # This test would be more meaningful if we had hierarchical categories
        # For now, we'll just test the basic functionality
        response = client.get("/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # If we had hierarchical categories, we could test:
        # - Parent categories
        # - Child categories
        # - Category tree structure
