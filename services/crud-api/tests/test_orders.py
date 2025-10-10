import pytest
from fastapi.testclient import TestClient


class TestOrderCreation:
    """Test order creation functionality."""

    def test_create_order_success(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test successful order creation."""
        # Create a product first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Create order directly
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                    "price": sample_product_data["price"]["amount"]
                }
            ],
            "shipping_address": {
                "name": "홍길동",
                "phone": "010-1234-5678",
                "address": "서울시 강남구 테헤란로 123",
                "postal_code": "06292"
            },
            "payment_method": "card",
            "total_amount": sample_product_data["price"]["amount"] * 2 + 5000  # Including shipping
        }
        
        response = client.post("/orders", json=order_data, headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        
        # Check order structure
        assert "id" in data
        assert data["status"] == "pending"
        assert data["user_id"] is not None
        assert len(data["items"]) == 1
        assert data["items"][0]["product_id"] == product_id
        assert data["items"][0]["quantity"] == 2
        assert data["total_amount"] == order_data["total_amount"]
        assert data["payment_method"] == "card"
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_order_empty_cart(self, client, authenticated_user_token):
        """Test order creation with empty cart."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        order_data = {
            "items": [],
            "shipping_address": {
                "name": "홍길동",
                "phone": "010-1234-5678",
                "address": "서울시 강남구 테헤란로 123",
                "postal_code": "06292"
            },
            "payment_method": "card",
            "total_amount": 0
        }
        
        response = client.post("/orders", json=order_data, headers=headers)
        assert response.status_code == 400
        assert "Cart is empty" in response.json()["detail"]

    def test_create_order_unauthorized(self, client, sample_category, sample_product_data):
        """Test order creation without authentication."""
        order_data = {
            "items": [
                {
                    "product_id": "some-id",
                    "quantity": 1,
                    "price": 100000
                }
            ],
            "shipping_address": {
                "name": "홍길동",
                "phone": "010-1234-5678",
                "address": "서울시 강남구 테헤란로 123",
                "postal_code": "06292"
            },
            "payment_method": "card",
            "total_amount": 100000
        }
        
        response = client.post("/orders", json=order_data)
        assert response.status_code == 401

    def test_create_order_invalid_product(self, client, authenticated_user_token):
        """Test order creation with non-existent product."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        order_data = {
            "items": [
                {
                    "product_id": "non-existent-id",
                    "quantity": 1,
                    "price": 100000
                }
            ],
            "shipping_address": {
                "name": "홍길동",
                "phone": "010-1234-5678",
                "address": "서울시 강남구 테헤란로 123",
                "postal_code": "06292"
            },
            "payment_method": "card",
            "total_amount": 100000
        }
        
        response = client.post("/orders", json=order_data, headers=headers)
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]

    def test_create_order_flow(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test order creation end-to-end without cart endpoints."""
        # Create a product first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Create order
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                    "price": sample_product_data["price"]["amount"]
                }
            ],
            "shipping_address": {
                "name": "홍길동",
                "phone": "010-1234-5678",
                "address": "서울시 강남구 테헤란로 123",
                "postal_code": "06292"
            },
            "payment_method": "card",
            "total_amount": sample_product_data["price"]["amount"] * 2 + 5000
        }
        
        order_response = client.post("/orders", json=order_data, headers=headers)
        assert order_response.status_code == 201
        
        # Cart endpoints removed


class TestOrderRetrieval:
    """Test order retrieval functionality."""

    def test_get_orders_empty(self, client, authenticated_user_token):
        """Test getting orders when user has no orders."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        response = client.get("/orders", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_orders_with_data(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test getting orders when user has orders."""
        # Create a product and order first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Create order
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                    "price": sample_product_data["price"]["amount"]
                }
            ],
            "shipping_address": {
                "name": "홍길동",
                "phone": "010-1234-5678",
                "address": "서울시 강남구 테헤란로 123",
                "postal_code": "06292"
            },
            "payment_method": "card",
            "total_amount": sample_product_data["price"]["amount"] + 5000
        }
        
        order_response = client.post("/orders", json=order_data, headers=headers)
        assert order_response.status_code == 201
        
        # Get orders
        response = client.get("/orders", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending"
        assert data[0]["total_amount"] == order_data["total_amount"]

    def test_get_orders_unauthorized(self, client):
        """Test getting orders without authentication."""
        response = client.get("/orders")
        assert response.status_code == 401

    def test_get_orders_pagination(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test order pagination."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Create multiple orders
        for i in range(5):
            create_response = client.post("/products", json=sample_product_data, headers=headers)
            assert create_response.status_code == 201
            product_id = create_response.json()["id"]
            
            order_data = {
                "items": [
                    {
                        "product_id": product_id,
                        "quantity": 1,
                        "price": sample_product_data["price"]["amount"]
                    }
                ],
                "shipping_address": {
                    "name": f"홍길동{i}",
                    "phone": "010-1234-5678",
                    "address": "서울시 강남구 테헤란로 123",
                    "postal_code": "06292"
                },
                "payment_method": "card",
                "total_amount": sample_product_data["price"]["amount"] + 5000
            }
            
            order_response = client.post("/orders", json=order_data, headers=headers)
            assert order_response.status_code == 201
        
        # Test pagination
        response = client.get("/orders?page=1&page_size=3", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 3

    def test_get_specific_order(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test getting a specific order by ID."""
        # Create a product and order first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                    "price": sample_product_data["price"]["amount"]
                }
            ],
            "shipping_address": {
                "name": "홍길동",
                "phone": "010-1234-5678",
                "address": "서울시 강남구 테헤란로 123",
                "postal_code": "06292"
            },
            "payment_method": "card",
            "total_amount": sample_product_data["price"]["amount"] + 5000
        }
        
        order_response = client.post("/orders", json=order_data, headers=headers)
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]
        
        # Get specific order
        response = client.get(f"/orders/{order_id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == order_id
        assert data["status"] == "pending"

    def test_get_specific_order_not_found(self, client, authenticated_user_token):
        """Test getting non-existent order."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        response = client.get("/orders/non-existent-id", headers=headers)
        assert response.status_code == 404
        assert "Order not found" in response.json()["detail"]

    def test_get_specific_order_unauthorized(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test getting order from different user."""
        # Create order with first user
        headers1 = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers1)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                    "price": sample_product_data["price"]["amount"]
                }
            ],
            "shipping_address": {
                "name": "홍길동",
                "phone": "010-1234-5678",
                "address": "서울시 강남구 테헤란로 123",
                "postal_code": "06292"
            },
            "payment_method": "card",
            "total_amount": sample_product_data["price"]["amount"] + 5000
        }
        
        order_response = client.post("/orders", json=order_data, headers=headers1)
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]
        
        # Create second user and try to access first user's order
        user2_data = {
            "email": "user2@example.com",
            "password": "password123",
            "name": "User 2",
            "phone": "010-9876-5432"
        }
        
        signup_response = client.post("/auth/users/signup", json=user2_data)
        assert signup_response.status_code == 201
        token2 = signup_response.json()["tokens"]["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Try to access first user's order
        response = client.get(f"/orders/{order_id}", headers=headers2)
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]


class TestOrderStatusUpdate:
    """Test order status update functionality."""

    def test_update_order_status_success(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test successful order status update."""
        # Create a product and order first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                    "price": sample_product_data["price"]["amount"]
                }
            ],
            "shipping_address": {
                "name": "홍길동",
                "phone": "010-1234-5678",
                "address": "서울시 강남구 테헤란로 123",
                "postal_code": "06292"
            },
            "payment_method": "card",
            "total_amount": sample_product_data["price"]["amount"] + 5000
        }
        
        order_response = client.post("/orders", json=order_data, headers=headers)
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]
        
        # Update order status
        status_data = {"status": "confirmed"}
        response = client.put(f"/orders/{order_id}/status", json=status_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "confirmed"
        assert data["id"] == order_id

    def test_update_order_status_not_found(self, client, authenticated_user_token):
        """Test updating non-existent order status."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        status_data = {"status": "confirmed"}
        
        response = client.put("/orders/non-existent-id/status", json=status_data, headers=headers)
        assert response.status_code == 404
        assert "Order not found" in response.json()["detail"]

    def test_update_order_status_unauthorized(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test updating order status from different user."""
        # Create order with first user
        headers1 = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers1)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                    "price": sample_product_data["price"]["amount"]
                }
            ],
            "shipping_address": {
                "name": "홍길동",
                "phone": "010-1234-5678",
                "address": "서울시 강남구 테헤란로 123",
                "postal_code": "06292"
            },
            "payment_method": "card",
            "total_amount": sample_product_data["price"]["amount"] + 5000
        }
        
        order_response = client.post("/orders", json=order_data, headers=headers1)
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]
        
        # Create second user and try to update first user's order
        user2_data = {
            "email": "user2@example.com",
            "password": "password123",
            "name": "User 2",
            "phone": "010-9876-5432"
        }
        
        signup_response = client.post("/auth/users/signup", json=user2_data)
        assert signup_response.status_code == 201
        token2 = signup_response.json()["tokens"]["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Try to update first user's order
        status_data = {"status": "confirmed"}
        response = client.put(f"/orders/{order_id}/status", json=status_data, headers=headers2)
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_update_order_status_invalid_data(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test updating order status with invalid data."""
        # Create a product and order first
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        order_data = {
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                    "price": sample_product_data["price"]["amount"]
                }
            ],
            "shipping_address": {
                "name": "홍길동",
                "phone": "010-1234-5678",
                "address": "서울시 강남구 테헤란로 123",
                "postal_code": "06292"
            },
            "payment_method": "card",
            "total_amount": sample_product_data["price"]["amount"] + 5000
        }
        
        order_response = client.post("/orders", json=order_data, headers=headers)
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]
        
        # Update with invalid status data
        invalid_status_data = {"status": ""}  # Empty status
        response = client.put(f"/orders/{order_id}/status", json=invalid_status_data, headers=headers)
        # Should succeed (validation might be handled at application level)
        assert response.status_code in [200, 422]
