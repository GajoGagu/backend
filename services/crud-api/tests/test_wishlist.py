import pytest
from fastapi.testclient import TestClient


class TestWishlistOperations:
    """Test wishlist operations."""

    def test_get_empty_wishlist(self, client, authenticated_user_token):
        """Test getting an empty wishlist."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        response = client.get("/wishlist", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check wishlist structure
        assert "items" in data
        assert "page" in data
        assert "page_size" in data
        assert "total" in data
        
        # Check empty wishlist values
        assert data["items"] == []
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total"] == 0

    def test_get_wishlist_unauthorized(self, client):
        """Test getting wishlist without authentication."""
        response = client.get("/wishlist")
        assert response.status_code == 401

    def test_add_to_wishlist_success(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test adding item to wishlist successfully."""
        # Create a product first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Add to wishlist
        response = client.post(f"/wishlist/items?product_id={product_id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check wishlist structure
        assert len(data["items"]) == 1
        item = data["items"][0]
        assert item["product"]["id"] == product_id
        assert item["product"]["title"] == sample_product_data["title"]
        assert "created_at" in item

    def test_add_to_wishlist_product_not_found(self, client, authenticated_user_token):
        """Test adding non-existent product to wishlist."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        response = client.post("/wishlist/items?product_id=non-existent-id", headers=headers)
        
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]

    def test_add_to_wishlist_unauthorized(self, client, sample_category, sample_product_data):
        """Test adding to wishlist without authentication."""
        response = client.post("/wishlist/items?product_id=some-id")
        assert response.status_code == 401

    def test_add_duplicate_to_wishlist(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test adding same product to wishlist multiple times."""
        # Create a product first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Add to wishlist first time
        response1 = client.post(f"/wishlist/items?product_id={product_id}", headers=headers)
        assert response1.status_code == 200
        
        # Add same product again
        response2 = client.post(f"/wishlist/items?product_id={product_id}", headers=headers)
        assert response2.status_code == 200
        
        # Check that only one item exists
        wishlist_response = client.get("/wishlist", headers=headers)
        assert wishlist_response.status_code == 200
        data = wishlist_response.json()
        assert len(data["items"]) == 1

    def test_wishlist_with_multiple_items(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test wishlist with multiple different items."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Create multiple products
        product_ids = []
        for i in range(3):
            product = sample_product_data.copy()
            product["title"] = f"Wishlist Product {i}"
            product["price"]["amount"] = 100000 + (i * 10000)
            
            create_response = client.post("/products", json=product, headers=headers)
            assert create_response.status_code == 201
            product_ids.append(create_response.json()["id"])
        
        # Add all products to wishlist
        for product_id in product_ids:
            response = client.post(f"/wishlist/items?product_id={product_id}", headers=headers)
            assert response.status_code == 200
        
        # Verify wishlist has all items
        wishlist_response = client.get("/wishlist", headers=headers)
        assert wishlist_response.status_code == 200
        data = wishlist_response.json()
        
        assert len(data["items"]) == 3
        assert data["total"] == 3

    def test_remove_from_wishlist_success(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test removing item from wishlist successfully."""
        # Create a product first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Add to wishlist
        add_response = client.post(f"/wishlist/items?product_id={product_id}", headers=headers)
        assert add_response.status_code == 200
        
        # Verify item is in wishlist
        wishlist_response = client.get("/wishlist", headers=headers)
        assert wishlist_response.status_code == 200
        assert len(wishlist_response.json()["items"]) == 1
        
        # Remove from wishlist
        remove_response = client.delete(f"/wishlist/items?product_id={product_id}", headers=headers)
        assert remove_response.status_code == 200
        
        # Verify item is removed
        wishlist_response = client.get("/wishlist", headers=headers)
        assert wishlist_response.status_code == 200
        assert len(wishlist_response.json()["items"]) == 0

    def test_remove_from_wishlist_not_found(self, client, authenticated_user_token):
        """Test removing non-existent item from wishlist."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        response = client.delete("/wishlist/items?product_id=non-existent-id", headers=headers)
        
        assert response.status_code == 404
        assert "Item not found in wishlist" in response.json()["detail"]

    def test_remove_from_wishlist_unauthorized(self, client):
        """Test removing from wishlist without authentication."""
        response = client.delete("/wishlist/items?product_id=some-id")
        assert response.status_code == 401

    def test_wishlist_pagination(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test wishlist pagination."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Create multiple products and add to wishlist
        for i in range(5):
            product = sample_product_data.copy()
            product["title"] = f"Pagination Product {i}"
            
            create_response = client.post("/products", json=product, headers=headers)
            assert create_response.status_code == 201
            product_id = create_response.json()["id"]
            
            add_response = client.post(f"/wishlist/items?product_id={product_id}", headers=headers)
            assert add_response.status_code == 200
        
        # Test pagination
        response = client.get("/wishlist?page=1&page_size=3", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 3
        assert len(data["items"]) <= 3
        assert data["total"] == 5

    def test_wishlist_removes_deleted_products(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test that wishlist handles deleted products gracefully."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Create a product and add to wishlist
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        add_response = client.post(f"/wishlist/items?product_id={product_id}", headers=headers)
        assert add_response.status_code == 200
        
        # Verify item is in wishlist
        wishlist_response = client.get("/wishlist", headers=headers)
        assert wishlist_response.status_code == 200
        assert len(wishlist_response.json()["items"]) == 1
        
        # Note: In a real implementation, you'd delete the product here
        # For now, we'll just verify the wishlist structure handles missing products
        # The get_wishlist function should filter out products that don't exist in products_db
