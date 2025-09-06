import uuid
from fastapi import APIRouter, HTTPException, Depends
from models import Cart, CartItem, Money, Product
from database import cart_db, products_db
from auth import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=Cart)
def get_cart(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    cart_data = cart_db.get(user_id, {"items": []})
    
    items = []
    subtotal = 0
    
    for item in cart_data["items"]:
        if item["product_id"] in products_db:
            product = Product(**products_db[item["product_id"]])
            line_total = product.price.amount * item["quantity"]
            subtotal += line_total
            
            items.append(CartItem(
                item_id=item["item_id"],
                product=product,
                quantity=item["quantity"],
                unit_price=product.price,
                line_total=Money(currency="KRW", amount=line_total)
            ))
    
    shipping_fee = Money(currency="KRW", amount=5000 if subtotal < 100000 else 0)
    grand_total = subtotal + shipping_fee.amount
    
    return Cart(
        items=items,
        subtotal=Money(currency="KRW", amount=subtotal),
        shipping_fee=shipping_fee,
        grand_total=Money(currency="KRW", amount=grand_total)
    )


@router.post("/items", response_model=Cart)
def add_to_cart(
    product_id: str,
    quantity: int = 1,
    current_user: dict = Depends(get_current_user)
):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    user_id = current_user["id"]
    if user_id not in cart_db:
        cart_db[user_id] = {"items": []}
    
    # Check if item already exists
    for item in cart_db[user_id]["items"]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            return get_cart(current_user)
    
    # Add new item
    item_id = str(uuid.uuid4())
    cart_db[user_id]["items"].append({
        "item_id": item_id,
        "product_id": product_id,
        "quantity": quantity
    })
    
    return get_cart(current_user)
