import pytest
from fastapi.testclient import TestClient


class TestE2EUserFlow:
    """Test end-to-end user flows."""

    def test_complete_user_journey(self, client, sample_user_data, sample_category, sample_product_data):
        """Test complete user journey: signup -> create product -> add to cart -> create order."""
        # 1. User signup
        signup_response = client.post("/auth/users/signup", json=sample_user_data)
        assert signup_response.status_code == 201
        user_token = signup_response.json()["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # 2. Create a product
        create_response = client.post("/products", json=sample_product_data, headers=headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # 3. Add product to cart
        cart_response = client.post(f"/cart/items?product_id={product_id}&quantity=2", headers=headers)
        assert cart_response.status_code == 200
        
        # 4. Verify cart contents
        cart_get_response = client.get("/cart", headers=headers)
        assert cart_get_response.status_code == 200
        cart_data = cart_get_response.json()
        assert len(cart_data["items"]) == 1
        assert cart_data["items"][0]["quantity"] == 2
        
        # 5. Create order
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
        order_id = order_response.json()["id"]
        
        # 6. Verify cart is cleared
        cart_get_response = client.get("/cart", headers=headers)
        assert cart_get_response.status_code == 200
        assert len(cart_get_response.json()["items"]) == 0
        
        # 7. Verify order exists
        orders_response = client.get("/orders", headers=headers)
        assert orders_response.status_code == 200
        orders = orders_response.json()
        assert len(orders) == 1
        assert orders[0]["id"] == order_id
        
        # 8. Update order status
        status_response = client.put(f"/orders/{order_id}/status", 
                                   json={"status": "confirmed"}, headers=headers)
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "confirmed"

    def test_multi_user_scenario(self, client, sample_user_data, sample_rider_data, sample_category, sample_product_data):
        """Test scenario with multiple users (user and rider)."""
        # 1. User signup and create product
        user_signup = client.post("/auth/users/signup", json=sample_user_data)
        assert user_signup.status_code == 201
        user_token = user_signup.json()["tokens"]["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        create_response = client.post("/products", json=sample_product_data, headers=user_headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # 2. Rider signup
        rider_signup = client.post("/auth/riders/signup", json=sample_rider_data)
        assert rider_signup.status_code == 201
        rider_token = rider_signup.json()["tokens"]["access_token"]
        rider_headers = {"Authorization": f"Bearer {rider_token}"}
        
        # 3. User adds product to cart and creates order
        cart_response = client.post(f"/cart/items?product_id={product_id}&quantity=1", headers=user_headers)
        assert cart_response.status_code == 200
        
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
        
        order_response = client.post("/orders", json=order_data, headers=user_headers)
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]
        
        # 4. Verify users can't access each other's data
        # Rider tries to access user's orders
        rider_orders = client.get("/orders", headers=rider_headers)
        assert rider_orders.status_code == 200
        assert rider_orders.json() == []  # Rider has no orders
        
        # User tries to access rider's orders (should be empty)
        user_orders = client.get("/orders", headers=user_headers)
        assert user_orders.status_code == 200
        assert len(user_orders.json()) == 1  # User has one order

    def test_product_search_and_filtering_flow(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test product search and filtering functionality."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Create multiple products with different characteristics
        products = []
        for i in range(5):
            product = sample_product_data.copy()
            product["title"] = f"Product {i} - {'Expensive' if i % 2 == 0 else 'Cheap'}"
            product["price"]["amount"] = 100000 + (i * 20000)  # Different prices
            product["description"] = f"Description for product {i}"
            
            create_response = client.post("/products", json=product, headers=headers)
            assert create_response.status_code == 201
            products.append(create_response.json())
        
        # Test search by title
        search_response = client.get("/products?q=Expensive")
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results["items"]) >= 2  # At least 2 expensive products
        
        # Test price filtering
        price_filter_response = client.get("/products?price_min=120000&price_max=160000")
        assert price_filter_response.status_code == 200
        price_results = price_filter_response.json()
        assert all(120000 <= item["price"]["amount"] <= 160000 for item in price_results["items"])
        
        # Test sorting
        sort_response = client.get("/products?sort=price_asc")
        assert sort_response.status_code == 200
        sort_results = sort_response.json()
        if len(sort_results["items"]) >= 2:
            prices = [item["price"]["amount"] for item in sort_results["items"]]
            assert prices == sorted(prices)
        
        # Test pagination
        page_response = client.get("/products?page=1&page_size=3")
        assert page_response.status_code == 200
        page_results = page_response.json()
        assert len(page_results["items"]) <= 3
        assert page_results["page"] == 1
        assert page_results["page_size"] == 3

    def test_cart_operations_flow(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test comprehensive cart operations."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Create multiple products
        product_ids = []
        for i in range(3):
            product = sample_product_data.copy()
            product["title"] = f"Cart Product {i}"
            product["price"]["amount"] = 50000 + (i * 10000)
            
            create_response = client.post("/products", json=product, headers=headers)
            assert create_response.status_code == 201
            product_ids.append(create_response.json()["id"])
        
        # Add different quantities of each product
        for i, product_id in enumerate(product_ids):
            quantity = i + 1
            response = client.post(f"/cart/items?product_id={product_id}&quantity={quantity}", headers=headers)
            assert response.status_code == 200
        
        # Verify cart contents
        cart_response = client.get("/cart", headers=headers)
        assert cart_response.status_code == 200
        cart_data = cart_response.json()
        
        assert len(cart_data["items"]) == 3
        assert cart_data["subtotal"]["amount"] == (50000 * 1) + (60000 * 2) + (70000 * 3)  # 320000
        assert cart_data["shipping_fee"]["amount"] == 0  # Above 100,000 threshold
        assert cart_data["grand_total"]["amount"] == 320000
        
        # Add more of existing item
        response = client.post(f"/cart/items?product_id={product_ids[0]}&quantity=2", headers=headers)
        assert response.status_code == 200
        
        # Verify quantity increased
        cart_response = client.get("/cart", headers=headers)
        cart_data = cart_response.json()
        first_item = next(item for item in cart_data["items"] if item["product"]["id"] == product_ids[0])
        assert first_item["quantity"] == 3  # 1 + 2


class TestErrorHandling:
    """Test error handling across the application."""

    def test_authentication_errors(self, client, sample_category, sample_product_data):
        """Test various authentication error scenarios."""
        # Try to access protected endpoints without token
        endpoints = [
            ("GET", "/cart"),
            ("POST", "/products"),
            ("GET", "/orders"),
            ("POST", "/orders"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            assert response.status_code == 401

    def test_validation_errors(self, client, authenticated_user_token, sample_category):
        """Test various validation error scenarios."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Invalid product data
        invalid_product = {
            "title": "",  # Empty title
            "description": "Test",
            "price": {
                "currency": "KRW",
                "amount": -100  # Negative price
            },
            "category_id": sample_category["id"],
            "location": {
                "address": "Test",
                "latitude": 200,  # Invalid latitude
                "longitude": 200  # Invalid longitude
            },
            "attributes": {}
        }
        
        response = client.post("/products", json=invalid_product, headers=headers)
        assert response.status_code == 422  # Validation error

    def test_not_found_errors(self, client, authenticated_user_token):
        """Test various not found error scenarios."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Non-existent product
        response = client.get("/products/non-existent-id")
        assert response.status_code == 404
        
        # Non-existent order
        response = client.get("/orders/non-existent-id", headers=headers)
        assert response.status_code == 404
        
        # Non-existent cart item
        response = client.post("/cart/items?product_id=non-existent-id&quantity=1", headers=headers)
        assert response.status_code == 404

    def test_permission_errors(self, client, sample_user_data, sample_category, sample_product_data):
        """Test permission/access control errors."""
        # Create two users
        user1_signup = client.post("/auth/users/signup", json=sample_user_data)
        assert user1_signup.status_code == 201
        user1_token = user1_signup.json()["tokens"]["access_token"]
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        
        user2_data = sample_user_data.copy()
        user2_data["email"] = "user2@example.com"
        user2_signup = client.post("/auth/users/signup", json=user2_data)
        assert user2_signup.status_code == 201
        user2_token = user2_signup.json()["tokens"]["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # User1 creates a product and order
        create_response = client.post("/products", json=sample_product_data, headers=user1_headers)
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        order_data = {
            "items": [{"product_id": product_id, "quantity": 1, "price": sample_product_data["price"]["amount"]}],
            "shipping_address": {"name": "Test", "phone": "010-1234-5678", "address": "Test", "postal_code": "12345"},
            "payment_method": "card",
            "total_amount": sample_product_data["price"]["amount"] + 5000
        }
        
        order_response = client.post("/orders", json=order_data, headers=user1_headers)
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]
        
        # User2 tries to access User1's order
        response = client.get(f"/orders/{order_id}", headers=user2_headers)
        assert response.status_code == 403
        
        # User2 tries to update User1's order
        response = client.put(f"/orders/{order_id}/status", json={"status": "confirmed"}, headers=user2_headers)
        assert response.status_code == 403


class TestPerformance:
    """Test performance-related scenarios."""

    def test_large_cart_operations(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test cart operations with many items."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Create many products
        product_ids = []
        for i in range(10):
            product = sample_product_data.copy()
            product["title"] = f"Performance Test Product {i}"
            product["price"]["amount"] = 10000 + (i * 1000)
            
            create_response = client.post("/products", json=product, headers=headers)
            assert create_response.status_code == 201
            product_ids.append(create_response.json()["id"])
        
        # Add all products to cart
        for product_id in product_ids:
            response = client.post(f"/cart/items?product_id={product_id}&quantity=1", headers=headers)
            assert response.status_code == 200
        
        # Verify cart can handle many items
        cart_response = client.get("/cart", headers=headers)
        assert cart_response.status_code == 200
        cart_data = cart_response.json()
        assert len(cart_data["items"]) == 10
        
        # Verify totals are calculated correctly
        expected_subtotal = sum(10000 + (i * 1000) for i in range(10))
        assert cart_data["subtotal"]["amount"] == expected_subtotal

    def test_pagination_performance(self, client, authenticated_user_token, sample_category, sample_product_data):
        """Test pagination with many items."""
        headers = {"Authorization": f"Bearer {authenticated_user_token}"}
        
        # Create many products
        for i in range(25):
            product = sample_product_data.copy()
            product["title"] = f"Pagination Test Product {i}"
            product["price"]["amount"] = 10000 + (i * 1000)
            
            create_response = client.post("/products", json=product, headers=headers)
            assert create_response.status_code == 201
        
        # Test different page sizes
        for page_size in [5, 10, 20]:
            response = client.get(f"/products?page=1&page_size={page_size}")
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) <= page_size
            assert data["page_size"] == page_size
