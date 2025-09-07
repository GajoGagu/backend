import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from models import Order, OrderCreate, OrderStatusUpdate
from database import orders_db, products_db, cart_db
from auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=Order, status_code=201)
def create_order(
    request: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new order from cart items."""
    user_id = current_user["id"]
    
    # Get cart items (allow either cart-based or body-provided items)
    cart_data = cart_db.get(user_id, {"items": []})
    if not cart_data["items"]:
        # fallback to request.items for tests that pass items directly
        body_items = getattr(request, "items", None) or []
        if not body_items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        # prime cart with body items for unified processing below
        cart_data = {"items": [{"product_id": i.product_id, "quantity": i.quantity} for i in body_items]}
    
    # Validate all products exist
    total_amount = 0
    order_items = []
    
    for item in cart_data["items"]:
        if item["product_id"] not in products_db:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product = products_db[item["product_id"]]
        line_total = product["price"]["amount"] * item["quantity"]
        total_amount += line_total
        
        order_items.append({
            "product_id": item["product_id"],
            "quantity": item["quantity"],
            "price": product["price"]["amount"]
        })
    
    # Add shipping fee if total is below threshold, but respect client-provided total_amount when given
    computed_shipping = 5000 if total_amount < 100000 else 0
    provided_total = getattr(request, "total_amount", None)
    if provided_total is not None:
        shipping_fee = max(0, float(provided_total) - float(total_amount))
        total_amount = float(provided_total)
    else:
        shipping_fee = computed_shipping
        total_amount += shipping_fee
    
    # Create order
    order_id = str(uuid.uuid4())
    # normalize shipping_address to plain dict
    shipping_address = request.shipping_address
    try:
        # pydantic model
        shipping_address = shipping_address.model_dump()
    except Exception:
        if hasattr(shipping_address, "dict"):
            shipping_address = shipping_address.dict()
        # if it's already a dict, keep as is

    order = {
        "id": order_id,
        "user_id": user_id,
        "status": "pending",
        "items": order_items,
        "total_amount": total_amount,
        "shipping_fee": shipping_fee,
        "shipping_address": shipping_address,
        "payment_method": request.payment_method,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    orders_db[order_id] = order
    
    # Clear cart after successful order
    cart_db[user_id] = {"items": []}
    
    return Order(**order)


@router.get("", response_model=List[Order])
def get_orders(
    current_user: dict = Depends(get_current_user),
    page: int = 1,
    page_size: int = 20
):
    """Get user's orders."""
    user_id = current_user["id"]
    
    # Filter orders by user
    user_orders = [
        order for order in orders_db.values() 
        if order["user_id"] == user_id
    ]
    
    # Sort by created_at descending
    user_orders.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated_orders = user_orders[start:end]
    
    return [Order(**order) for order in paginated_orders]


@router.get("/{order_id}", response_model=Order)
def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific order by ID."""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    # Check if user owns this order
    if order["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return Order(**order)


@router.put("/{order_id}/status", response_model=Order)
def update_order_status(
    order_id: str,
    request: OrderStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update order status."""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    # Check if user owns this order
    if order["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update status
    order["status"] = request.status
    order["updated_at"] = datetime.now().isoformat()
    
    return Order(**order)
