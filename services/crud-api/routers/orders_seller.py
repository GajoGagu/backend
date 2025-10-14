import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Order, OrderStatusUpdate
from database.config import get_db
from database.service import DatabaseService
from auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders-seller"])


@router.get("/seller", response_model=List[Order])
def get_seller_orders(
    current_user: dict = Depends(get_current_user),
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """판매자가 자신의 상품에 대한 주문 목록 조회"""
    service = DatabaseService(db)
    from database.models import Order as OrderModel, OrderItem as OrderItemModel, Product as ProductModel
    
    # 현재 사용자의 상품들에 대한 주문만 조회
    subquery = db.query(OrderItemModel.order_id).join(
        ProductModel, OrderItemModel.product_id == ProductModel.id
    ).filter(ProductModel.seller_id == current_user["id"]).subquery()
    
    q = db.query(OrderModel).filter(
        OrderModel.id.in_(subquery)
    ).order_by(OrderModel.created_at.desc())
    
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
            delivery_type=r.delivery_type,
            created_at=r.created_at.isoformat() if r.created_at else "",
            updated_at=r.updated_at.isoformat() if r.updated_at else "",
        ))
    return orders


@router.put("/{order_id}/seller-status", response_model=Order)
def update_order_status_by_seller(
    order_id: str,
    request: OrderStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """판매자가 주문 상태 변경 (paid, shipping, completed, cancelled)"""
    from database.models import Order as OrderModel, OrderItem as OrderItemModel, Product as ProductModel
    service = DatabaseService(db)
    
    r = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 판매자 권한 확인: 주문에 포함된 상품 중 하나라도 현재 사용자가 판매자인지 확인
    order_items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).all()
    is_seller = False
    for item in order_items:
        product = service.get_product_by_id(item.product_id)
        if product and product.seller_id == current_user["id"]:
            is_seller = True
            break
    
    if not is_seller:
        raise HTTPException(status_code=403, detail="Only the seller can update order status")
    
    # 주문 상태 유효성 검사 (판매자는 paid, shipping, completed, cancelled만 가능)
    valid_seller_statuses = ["paid", "shipping", "completed", "cancelled"]
    if request.status not in valid_seller_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Seller can only set: {valid_seller_statuses}")
    
    r.status = request.status
    db.commit()
    
    # 주문 상태 변경 시 구매자에게 알림 전송
    status_messages = {
        "paid": "결제가 확인되었습니다!",
        "shipping": "배송이 시작되었습니다!",
        "completed": "구매가 완료되었습니다!",
        "cancelled": "주문이 취소되었습니다."
    }
    
    if request.status in status_messages:
        service.create_notification(
            user_id=r.user_id,
            title=status_messages[request.status],
            message=f"주문 #{r.id[:8]}...의 상태가 '{request.status}'로 변경되었습니다.",
            type="order_status"
        )
    
    items = db.query(OrderItemModel).filter(OrderItemModel.order_id == r.id).all()
    return Order(
        id=r.id,
        user_id=r.user_id,
        status=r.status,
        items=[{"product_id": it.product_id, "quantity": it.quantity, "price": it.price} for it in items],
        total_amount=r.total_amount,
        shipping_fee=0,
        shipping_address=r.shipping_address,
        delivery_type=r.delivery_type,
        created_at=r.created_at.isoformat() if r.created_at else "",
        updated_at=r.updated_at.isoformat() if r.updated_at else "",
    )
