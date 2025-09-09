import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Cart, CartItem, Money, Product
from database.config import get_db
from database.service import DatabaseService
from auth import get_current_user
from pydantic import BaseModel
class AddToCartRequest(BaseModel):
    product_id: str
    quantity: int = 1


router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=Cart)
def get_cart(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    service = DatabaseService(db)
    cart_items = service.get_user_cart(current_user["id"]) or []

    items = []
    subtotal = 0

    for item in cart_items:
        p = item.product
        if not p:
            continue
        unit_price = Money(currency=p.price_currency, amount=p.price_amount)
        line_total = unit_price.amount * item.quantity
        subtotal += line_total
        items.append(CartItem(
            item_id=item.id,
            product=Product(
                id=p.id,
                title=p.title,
                description=p.description,
                price={"currency": p.price_currency, "amount": p.price_amount},
                images=p.images or [],
                category={"id": p.category.id if p.category else p.category_id, "name": p.category.name if p.category else "", "parent_id": p.category.parent_id if p.category else None},
                seller_id=p.seller_id,
                location=p.location or {},
                attributes=p.attributes or {},
                stock=p.stock or 1,
                is_featured=bool(p.is_featured),
                likes_count=p.likes_count or 0,
                created_at=p.created_at.isoformat() if p.created_at else "",
            ),
            quantity=item.quantity,
            unit_price=unit_price,
            line_total=Money(currency="KRW", amount=line_total)
        ))

    shipping_fee_amount = 5000 if (subtotal == 0 or (subtotal < 100000 and subtotal > 0)) else 0
    shipping_fee = Money(currency="KRW", amount=shipping_fee_amount)
    grand_total = subtotal + shipping_fee.amount

    return Cart(
        items=items,
        subtotal=Money(currency="KRW", amount=subtotal),
        shipping_fee=shipping_fee,
        grand_total=Money(currency="KRW", amount=grand_total)
    )


@router.post("/items", response_model=Cart, status_code=201)
def add_to_cart(
    product_id: str,
    quantity: int = 1,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = DatabaseService(db)
    product = service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    service.add_to_cart(current_user["id"], product_id, quantity)
    return get_cart(current_user, db)


@router.post("/clear", response_model=Cart)
def clear_cart(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    service = DatabaseService(db)
    service.clear_user_cart(current_user["id"])
    return get_cart(current_user, db)
