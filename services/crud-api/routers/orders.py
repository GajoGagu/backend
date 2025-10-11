import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Order, OrderCreate, OrderStatusUpdate
from models.rider import RiderDeliveryResponse, RiderDeliveryListResponse
from database.config import get_db
from database.service import DatabaseService
from auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=Order, status_code=201)
def create_order(
    request: OrderCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order from cart items using DB."""
    service = DatabaseService(db)

    # Compute totals from body-provided items only (cart removed)
    body_items = getattr(request, "items", None) or []
    if not body_items:
        raise HTTPException(status_code=400, detail="Items are required")
    validated_items = []
    total_amount = 0
    for i in body_items:
        p = service.get_product_by_id(i.product_id)
        if not p:
            raise HTTPException(status_code=404, detail="Product not found")
        total_amount += (p.price_amount * i.quantity)
        validated_items.append({"product_id": p.id, "quantity": i.quantity, "price": p.price_amount})

    computed_shipping = 5000 if total_amount < 100000 else 0
    provided_total = getattr(request, "total_amount", None)
    if provided_total is not None:
        shipping_fee = max(0, float(provided_total) - float(total_amount))
        total_amount = float(provided_total)
    else:
        shipping_fee = computed_shipping
        total_amount += shipping_fee

    # Normalize shipping address
    shipping_address = request.shipping_address
    try:
        shipping_address = shipping_address.model_dump()
    except Exception:
        if hasattr(shipping_address, "dict"):
            shipping_address = shipping_address.dict()

    # Persist order and items
    order_id = str(uuid.uuid4())
    from database.models import Order as OrderModel, OrderItem as OrderItemModel
    order_row = OrderModel(
        id=order_id,
        user_id=current_user["id"],
        status="pending",
        total_amount=total_amount,
        total_currency="KRW",
        shipping_address=shipping_address,
        payment_method=request.payment_method,
    )
    db.add(order_row)
    db.flush()
    for it in validated_items:
        db.add(OrderItemModel(
            id=str(uuid.uuid4()),
            order_id=order_row.id,
            product_id=it["product_id"],
            quantity=it["quantity"],
            price=it["price"],
        ))
    db.commit()
    db.refresh(order_row)

    # Cart feature removed: nothing to clear

    return Order(
        id=order_row.id,
        user_id=order_row.user_id,
        status=order_row.status,
        items=[{"product_id": it["product_id"], "quantity": it["quantity"], "price": it["price"]} for it in validated_items],
        total_amount=order_row.total_amount,
        shipping_fee=shipping_fee,
        shipping_address=order_row.shipping_address,
        payment_method=order_row.payment_method,
        created_at=order_row.created_at.isoformat() if order_row.created_at else "",
        updated_at=order_row.updated_at.isoformat() if order_row.updated_at else "",
    )


@router.get("", response_model=List[Order])
def get_orders(
    current_user: dict = Depends(get_current_user),
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    service = DatabaseService(db)
    # simple query; could add sorting/pagination in DB
    from database.models import Order as OrderModel, OrderItem as OrderItemModel
    q = db.query(OrderModel).filter(OrderModel.user_id == current_user["id"]).order_by(OrderModel.created_at.desc())
    rows = q.offset((page - 1) * page_size).limit(page_size).all()

    orders: List[Order] = []
    for r in rows:
        items = db.query(OrderItemModel).filter(OrderItemModel.order_id == r.id).all()
        orders.append(Order(
            id=r.id,
            user_id=r.user_id,
            status=r.status,
            items=[{"product_id": it.product_id, "quantity": it.quantity, "price": it.price} for it in items],
            total_amount=r.total_amount,
            shipping_fee=0,  # not stored; computed earlier
            shipping_address=r.shipping_address,
            payment_method=r.payment_method,
            created_at=r.created_at.isoformat() if r.created_at else "",
            updated_at=r.updated_at.isoformat() if r.updated_at else "",
        ))
    return orders


@router.get("/{order_id}", response_model=Order)
def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from database.models import Order as OrderModel, OrderItem as OrderItemModel
    r = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Order not found")
    if r.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    items = db.query(OrderItemModel).filter(OrderItemModel.order_id == r.id).all()
    return Order(
        id=r.id,
        user_id=r.user_id,
        status=r.status,
        items=[{"product_id": it.product_id, "quantity": it.quantity, "price": it.price} for it in items],
        total_amount=r.total_amount,
        shipping_fee=0,
        shipping_address=r.shipping_address,
        payment_method=r.payment_method,
        created_at=r.created_at.isoformat() if r.created_at else "",
        updated_at=r.updated_at.isoformat() if r.updated_at else "",
    )


@router.put("/{order_id}/status", response_model=Order)
def update_order_status(
    order_id: str,
    request: OrderStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from database.models import Order as OrderModel, OrderItem as OrderItemModel
    r = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Order not found")
    if r.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    r.status = request.status
    db.commit()
    items = db.query(OrderItemModel).filter(OrderItemModel.order_id == r.id).all()
    return Order(
        id=r.id,
        user_id=r.user_id,
        status=r.status,
        items=[{"product_id": it.product_id, "quantity": it.quantity, "price": it.price} for it in items],
        total_amount=r.total_amount,
        shipping_fee=0,
        shipping_address=r.shipping_address,
        payment_method=r.payment_method,
        created_at=r.created_at.isoformat() if r.created_at else "",
        updated_at=r.updated_at.isoformat() if r.updated_at else "",
    )
