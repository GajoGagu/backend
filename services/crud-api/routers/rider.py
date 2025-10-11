from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.rider import (
    RiderDeliveryRequest, RiderDeliveryResponse, OrderWithDetails,
    DeliveryStatusUpdate, RiderDeliveryListResponse
)
from models.auth import User
from models.product import SellerInfo
from auth import get_current_user
from database.config import get_db
from database.service import DatabaseService

router = APIRouter(prefix="/rider", tags=["rider"])


@router.get("/available-orders", response_model=List[OrderWithDetails])
def get_available_orders_for_delivery(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """배송 가능한 주문 목록 조회 (라이더용)"""
    service = DatabaseService(db)
    
    # 라이더 권한 확인 (role이 rider인지 확인)
    if current_user.get("role") != "rider":
        raise HTTPException(status_code=403, detail="Only riders can access this endpoint")
    
    orders = service.get_available_orders_for_delivery()
    order_details = []
    
    for order in orders:
        # 구매자 정보
        buyer = service.get_user_by_id(order.user_id)
        if not buyer:
            continue
            
        buyer_info = User(
            id=buyer.id,
            role=buyer.role,
            email=buyer.email,
            name=buyer.name,
            phone=buyer.phone,
            address=buyer.address,
            kakao_open_profile=buyer.kakao_open_profile,
            created_at=buyer.created_at.isoformat() if buyer.created_at else ""
        )
        
        # 판매자 정보 (첫 번째 상품의 판매자)
        if not order.items:
            continue
            
        first_item = order.items[0]
        product = service.get_product_by_id(first_item.product_id)
        if not product:
            continue
            
        seller = service.get_user_by_id(product.seller_id)
        if not seller:
            continue
            
        seller_info = User(
            id=seller.id,
            role=seller.role,
            email=seller.email,
            name=seller.name,
            phone=seller.phone,
            address=seller.address,
            kakao_open_profile=seller.kakao_open_profile,
            created_at=seller.created_at.isoformat() if seller.created_at else ""
        )
        
        # 상품 정보
        product_info = {
            "id": product.id,
            "title": product.title,
            "description": product.description,
            "price": {
                "currency": product.price_currency,
                "amount": product.price_amount
            },
            "images": product.images or []
        }
        
        order_details.append(OrderWithDetails(
            order_id=order.id,
            buyer_info=buyer_info,
            seller_info=seller_info,
            product_info=product_info,
            total_amount=order.total_amount,
            created_at=order.created_at.isoformat() if order.created_at else ""
        ))
    
    return order_details


@router.post("/delivery-request", response_model=RiderDeliveryResponse, status_code=201)
def create_delivery_request(
    request: RiderDeliveryRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """라이더 배송 신청"""
    service = DatabaseService(db)
    
    # 라이더 권한 확인
    if current_user.get("role") != "rider":
        raise HTTPException(status_code=403, detail="Only riders can create delivery requests")
    
    try:
        delivery = service.create_rider_delivery(
            order_id=request.order_id,
            rider_id=current_user["id"],
            delivery_fee=request.delivery_fee
        )
        
        # 구매자에게 라이더 배송 신청 알림 전송
        order = service.get_order_with_details(request.order_id)
        if order:
            service.create_notification(
                user_id=order.user_id,
                title="라이더가 배송을 신청했습니다!",
                message=f"주문 #{request.order_id[:8]}...에 대한 라이더 배송 신청이 들어왔습니다. 배송비: {request.delivery_fee:,}원",
                type="delivery_request"
            )
        
        # 판매자와 구매자 정보를 User 모델로 변환
        seller_info = User(
            id=delivery.seller_info["id"],
            role="user",
            email="",  # 이메일은 보안상 제외
            name=delivery.seller_info["name"],
            phone=delivery.seller_info["phone"],
            address=delivery.seller_info["address"],
            kakao_open_profile=delivery.seller_info["kakao_open_profile"],
            created_at=""
        )
        
        buyer_info = User(
            id=delivery.buyer_info["id"],
            role="user", 
            email="",  # 이메일은 보안상 제외
            name=delivery.buyer_info["name"],
            phone=delivery.buyer_info["phone"],
            address=delivery.buyer_info["address"],
            kakao_open_profile=delivery.buyer_info["kakao_open_profile"],
            created_at=""
        )
        
        return RiderDeliveryResponse(
            id=delivery.id,
            order_id=delivery.order_id,
            rider_id=delivery.rider_id,
            delivery_fee=delivery.delivery_fee,
            status=delivery.status,
            seller_info=seller_info,
            buyer_info=buyer_info,
            created_at=delivery.created_at.isoformat() if delivery.created_at else "",
            updated_at=delivery.updated_at.isoformat() if delivery.updated_at else None
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my-deliveries", response_model=RiderDeliveryListResponse)
def get_my_deliveries(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """내 배송 신청 목록 조회"""
    service = DatabaseService(db)
    
    # 라이더 권한 확인
    if current_user.get("role") != "rider":
        raise HTTPException(status_code=403, detail="Only riders can access this endpoint")
    
    deliveries = service.get_rider_deliveries(current_user["id"])
    
    delivery_responses = []
    for delivery in deliveries:
        # 판매자와 구매자 정보를 User 모델로 변환
        seller_info = User(
            id=delivery.seller_info["id"],
            role="user",
            email="",  # 이메일은 보안상 제외
            name=delivery.seller_info["name"],
            phone=delivery.seller_info["phone"],
            address=delivery.seller_info["address"],
            kakao_open_profile=delivery.seller_info["kakao_open_profile"],
            created_at=""
        )
        
        buyer_info = User(
            id=delivery.buyer_info["id"],
            role="user",
            email="",  # 이메일은 보안상 제외
            name=delivery.buyer_info["name"],
            phone=delivery.buyer_info["phone"],
            address=delivery.buyer_info["address"],
            kakao_open_profile=delivery.buyer_info["kakao_open_profile"],
            created_at=""
        )
        
        delivery_responses.append(RiderDeliveryResponse(
            id=delivery.id,
            order_id=delivery.order_id,
            rider_id=delivery.rider_id,
            delivery_fee=delivery.delivery_fee,
            status=delivery.status,
            seller_info=seller_info,
            buyer_info=buyer_info,
            created_at=delivery.created_at.isoformat() if delivery.created_at else "",
            updated_at=delivery.updated_at.isoformat() if delivery.updated_at else None
        ))
    
    return RiderDeliveryListResponse(
        items=delivery_responses,
        total=len(delivery_responses)
    )


@router.put("/delivery/{delivery_id}/status", response_model=RiderDeliveryResponse)
def update_delivery_status(
    delivery_id: str,
    request: DeliveryStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """배송 상태 업데이트"""
    service = DatabaseService(db)
    
    # 라이더 권한 확인
    if current_user.get("role") != "rider":
        raise HTTPException(status_code=403, detail="Only riders can update delivery status")
    
    # 배송 신청이 해당 라이더의 것인지 확인
    delivery = service.get_rider_delivery_by_id(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery request not found")
    
    if delivery.rider_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="You can only update your own delivery requests")
    
    updated_delivery = service.update_delivery_status(delivery_id, request.status)
    if not updated_delivery:
        raise HTTPException(status_code=500, detail="Failed to update delivery status")
    
    # 판매자와 구매자 정보를 User 모델로 변환
    seller_info = User(
        id=updated_delivery.seller_info["id"],
        role="user",
        email="",  # 이메일은 보안상 제외
        name=updated_delivery.seller_info["name"],
        phone=updated_delivery.seller_info["phone"],
        address=updated_delivery.seller_info["address"],
        kakao_open_profile=updated_delivery.seller_info["kakao_open_profile"],
        created_at=""
    )
    
    buyer_info = User(
        id=updated_delivery.buyer_info["id"],
        role="user",
        email="",  # 이메일은 보안상 제외
        name=updated_delivery.buyer_info["name"],
        phone=updated_delivery.buyer_info["phone"],
        address=updated_delivery.buyer_info["address"],
        kakao_open_profile=updated_delivery.buyer_info["kakao_open_profile"],
        created_at=""
    )
    
    return RiderDeliveryResponse(
        id=updated_delivery.id,
        order_id=updated_delivery.order_id,
        rider_id=updated_delivery.rider_id,
        delivery_fee=updated_delivery.delivery_fee,
        status=updated_delivery.status,
        seller_info=seller_info,
        buyer_info=buyer_info,
        created_at=updated_delivery.created_at.isoformat() if updated_delivery.created_at else "",
        updated_at=updated_delivery.updated_at.isoformat() if updated_delivery.updated_at else None
    )
