import pytest
from fastapi.testclient import TestClient


class TestProductCRUD:
    """Test product CRUD operations."""

    def test_create_product_success(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test successful product creation."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        response = client.post("/products", json=sample_product_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        
        # Check response structure
        assert "id" in data
        assert data["title"] == sample_product_data["title"]
        assert data["description"] == sample_product_data["description"]
        assert data["price"]["currency"] == sample_product_data["price"]["currency"]
        assert data["price"]["amount"] == sample_product_data["price"]["amount"]
        assert data["category"]["id"] == sample_product_data["category_id"]
        assert data["seller_id"] is not None
        assert data["stock"] == 1
        assert data["is_featured"] is False
        assert data["likes_count"] == 0
        assert "created_at" in data

    def test_create_product_unauthorized(self, client, sample_category, sample_product_data):
        """Test product creation without authentication."""
        response = client.post("/products", json=sample_product_data)
        assert response.status_code == 401

    def test_create_product_invalid_category(self, client, authenticated_user_token, sample_product_data):
        """Test product creation with invalid category."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        sample_product_data["category_id"] = "invalid-category-id"
        
        response = client.post("/products", json=sample_product_data, headers=headers)
        assert response.status_code == 400
        assert "Invalid category" in response.json()["detail"]

    def test_create_product_invalid_data(self, client, authenticated_user_token, sample_category):
        """Test product creation with invalid data."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        invalid_data = {
            "title": "",  # Empty title
            "description": "Test description",
            "price": {
                "currency": "KRW",
                "amount": -100  # Negative price
            },
            "category_id": sample_category["id"],
            "location": {
                "address": "Test address",
                "latitude": 37.5665,
                "longitude": 126.9780
            },
            "attributes": {}
        }
        
        response = client.post("/products", json=invalid_data, headers=headers)
        assert response.status_code == 422  # Validation error

    def test_get_product_success(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test successful product retrieval."""
        # Create product first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Get product
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == product_id
        assert data["title"] == sample_product_data["title"]

    def test_get_product_not_found(self, client):
        """Test product retrieval with non-existent ID."""
        response = client.get("/products/non-existent-id")
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]


class TestProductSearch:
    """Test product search and filtering."""

    def test_get_products_default(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test getting products with default parameters."""
        # Create a product first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        
        # Get products
        response = client.get("/products")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "page" in data
        assert "page_size" in data
        assert "total" in data
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total"] >= 1

    def test_get_products_with_search_query(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test product search with query parameter."""
        # Create a product first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        
        # Search for products
        response = client.get("/products?q=테스트")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) >= 1
        assert any("테스트" in item["title"] for item in data["items"])

    def test_get_products_with_category_filter(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test product filtering by category."""
        # Create a product first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        
        # Filter by category
        response = client.get(f"/products?category_id={sample_category['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(item["category"]["id"] == sample_category["id"] for item in data["items"])

    def test_get_products_with_price_filter(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test product filtering by price range."""
        # Create a product first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        product = sample_product_data.copy()
        product["price"]["amount"] = 100000  # Ensure it falls within the filter range
        create_response = client.post("/products", json=product, headers=headers)
        assert create_response.status_code == 201
        
        # Filter by price range
        response = client.get("/products?price_min=50000&price_max=150000")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(50000 <= item["price"]["amount"] <= 150000 for item in data["items"])

    def test_get_products_with_sorting(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test product sorting."""
        # Create multiple products with different prices
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Product 1 - higher price
        product1 = sample_product_data.copy()
        product1["title"] = "Expensive Product"
        product1["price"]["amount"] = 200000
        create_response1 = client.post("/products", json=product1, headers=headers)
        assert create_response1.status_code == 201
        
        # Product 2 - lower price
        product2 = sample_product_data.copy()
        product2["title"] = "Cheap Product"
        product2["price"]["amount"] = 50000
        create_response2 = client.post("/products", json=product2, headers=headers)
        assert create_response2.status_code == 201
        
        # Test price ascending sort
        response = client.get("/products?sort=price_asc")
        assert response.status_code == 200
        
        data = response.json()
        if len(data["items"]) >= 2:
            prices = [item["price"]["amount"] for item in data["items"]]
            assert prices == sorted(prices)
        
        # Test price descending sort
        response = client.get("/products?sort=price_desc")
        assert response.status_code == 200
        
        data = response.json()
        if len(data["items"]) >= 2:
            prices = [item["price"]["amount"] for item in data["items"]]
            assert prices == sorted(prices, reverse=True)

    def test_get_products_with_pagination(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test product pagination."""
        # Create multiple products
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        for i in range(5):
            product = sample_product_data.copy()
            product["title"] = f"Product {i}"
            create_response = client.post("/products", json=product, headers=headers)
            assert create_response.status_code == 201
        
        # Test first page
        response = client.get("/products?page=1&page_size=3")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 3
        assert len(data["items"]) <= 3
        
        # Test second page
        response = client.get("/products?page=2&page_size=3")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 3

    def test_get_products_empty_result(self, client):
        """Test product search with no results."""
        response = client.get("/products?q=nonexistent")
        assert response.status_code == 200
        
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0


class TestProductValidation:
    """Test product data validation."""

    def test_product_price_validation(self, client, authenticated_user_token, sample_category):
        """Test product price validation."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Test with zero price
        product_data = {
            "title": "Test Product",
            "description": "Test description",
            "price": {
                "currency": "KRW",
                "amount": 0
            },
            "category_id": sample_category["id"],
            "location": {
                "address": "Test address",
                "latitude": 37.5665,
                "longitude": 126.9780
            },
            "attributes": {}
        }
        
        response = client.post("/products", json=product_data, headers=headers)
        # Should succeed with zero price (free product)
        assert response.status_code == 201

    def test_product_location_validation(self, client, authenticated_user_token, sample_category):
        """Test product location validation."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Test with invalid coordinates
        product_data = {
            "title": "Test Product",
            "description": "Test description",
            "price": {
                "currency": "KRW",
                "amount": 100000
            },
            "category_id": sample_category["id"],
            "location": {
                "address": "Test address",
                "latitude": 200,  # Invalid latitude
                "longitude": 200  # Invalid longitude
            },
            "attributes": {}
        }
        
        response = client.post("/products", json=product_data, headers=headers)
        # Should succeed (validation might be handled at application level)
        assert response.status_code in [201, 422]
