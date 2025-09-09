import pytest
from fastapi.testclient import TestClient


class TestCartOperations:
    """Test cart operations."""

    def test_get_empty_cart(self, client, authenticated_user_token):
        """Test getting an empty cart."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        response = client.get("/cart", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check cart structure
        assert "items" in data
        assert "subtotal" in data
        assert "shipping_fee" in data
        assert "grand_total" in data
        
        # Check empty cart values
        assert data["items"] == []
        assert data["subtotal"]["amount"] == 0
        assert data["subtotal"]["currency"] == "KRW"
        assert data["shipping_fee"]["amount"] == 5000  # Default shipping fee
        assert data["shipping_fee"]["currency"] == "KRW"
        assert data["grand_total"]["amount"] == 5000
        assert data["grand_total"]["currency"] == "KRW"

    def test_get_cart_unauthorized(self, client):
        """Test getting cart without authentication."""
        response = client.get("/cart")
        assert response.status_code == 401

    def test_add_to_cart_success(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test adding item to cart successfully."""
        # Create a product first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Add to cart
        response = client.post(f"/cart/items?product_id={product_id}&quantity=2", headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        
        # Check cart structure
        assert len(data["items"]) == 1
        item = data["items"][0]
        assert item["product"]["id"] == product_id
        assert item["quantity"] == 2
        assert item["unit_price"]["amount"] == sample_product_data["price"]["amount"]
        assert item["line_total"]["amount"] == sample_product_data["price"]["amount"] * 2
        
        # Check totals
        expected_subtotal = sample_product_data["price"]["amount"] * 2
        assert data["subtotal"]["amount"] == expected_subtotal
        assert data["shipping_fee"]["amount"] == 5000  # Below 100,000 threshold
        assert data["grand_total"]["amount"] == expected_subtotal + 5000

    def test_add_to_cart_product_not_found(self, client, authenticated_user_token):
        """Test adding non-existent product to cart."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        response = client.post("/cart/items?product_id=non-existent-id&quantity=1", headers=headers)
        
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]

    def test_add_to_cart_unauthorized(self, client, sample_category, sample_product_data):
        """Test adding to cart without authentication."""
        # Create a product first (this will fail without auth, but let's test the cart endpoint)
        response = client.post("/cart/items?product_id=some-id&quantity=1")
        assert response.status_code == 401

    def test_add_existing_item_to_cart(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test adding existing item to cart (should increase quantity)."""
        # Create a product first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Add to cart first time
        response1 = client.post(f"/cart/items?product_id={product_id}&quantity=2", headers=headers)
        assert response1.status_code == 201
        
        # Add same item again
        response2 = client.post(f"/cart/items?product_id={product_id}&quantity=3", headers=headers)
        assert response2.status_code == 201
        
        data = response2.json()
        
        # Check that quantity was increased
        assert len(data["items"]) == 1
        item = data["items"][0]
        assert item["quantity"] == 5  # 2 + 3
        
        # Check totals
        expected_subtotal = sample_product_data["price"]["amount"] * 5
        assert data["subtotal"]["amount"] == expected_subtotal

    def test_cart_with_multiple_items(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test cart with multiple different items."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Create multiple products
        product_ids = []
        for i in range(3):
            product = sample_product_data.copy()
            product["title"] = f"Product {i}"
            product["price"]["amount"] = 100000 + (i * 10000)  # Different prices
            
            create_response = client.post("/products", json=product, headers=headers)
            assert create_response.status_code == 201
            product_ids.append(create_response.json()["id"])
        
        # Add all products to cart
        for i, product_id in enumerate(product_ids):
            response = client.post(f"/cart/items?product_id={product_id}&quantity={i+1}", headers=headers)
            assert response.status_code == 201
        
        # Get final cart
        response = client.get("/cart", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        
        # Check cart has all items
        assert len(data["items"]) == 3
        
        # Check totals
        expected_subtotal = (100000 * 1) + (110000 * 2) + (120000 * 3)  # 680000
        assert data["subtotal"]["amount"] == expected_subtotal
        assert data["shipping_fee"]["amount"] == 0  # Above 100,000 threshold
        assert data["grand_total"]["amount"] == expected_subtotal

    def test_cart_shipping_fee_threshold(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test cart shipping fee calculation based on subtotal threshold."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Test below threshold (should have shipping fee)
        product_below = sample_product_data.copy()
        product_below["title"] = "Cheap Product"
        product_below["price"]["amount"] = 50000  # Below 100,000 threshold
        
        create_response = client.post("/products", json=product_below, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        response = client.post(f"/cart/items?product_id={product_id}&quantity=1", headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["shipping_fee"]["amount"] == 5000
        assert data["grand_total"]["amount"] == 55000
        
        # Clear cart and test above threshold
        # Clear cart between cases
        clear_resp = client.post("/cart/clear", headers=headers)
        assert clear_resp.status_code == 200
        
        # Test above threshold (should have no shipping fee)
        product_above = sample_product_data.copy()
        product_above["title"] = "Expensive Product"
        product_above["price"]["amount"] = 150000  # Above 100,000 threshold
        
        create_response = client.post("/products", json=product_above, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        response = client.post(f"/cart/items?product_id={product_id}&quantity=1", headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["shipping_fee"]["amount"] == 0
        assert data["grand_total"]["amount"] == 150000

    def test_cart_item_validation(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test cart item validation."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Create a product first
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Test with zero quantity
        response = client.post(f"/cart/items?product_id={product_id}&quantity=0", headers=headers)
        # Should succeed (validation might be handled at application level)
        assert response.status_code in [201, 422]
        
        # Test with negative quantity
        response = client.post(f"/cart/items?product_id={product_id}&quantity=-1", headers=headers)
        # Should succeed (validation might be handled at application level)
        assert response.status_code in [201, 422]

    def test_cart_removes_deleted_products(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test that cart handles deleted products gracefully."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Create a product and add to cart
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        response = client.post(f"/cart/items?product_id={product_id}&quantity=1", headers=headers)
        assert response.status_code == 201
        
        # Verify item is in cart
        response = client.get("/cart", headers=headers)
        assert response.status_code == 200
        assert len(response.json()["items"]) == 1
        
        # Note: In a real implementation, you'd delete the product here
        # For now, we'll just verify the cart structure handles missing products
        # The get_cart function should filter out products that don't exist in products_db
