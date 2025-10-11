from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.rider import RiderDeliveryResponse, RiderDeliveryListResponse
from models.auth import User
from database.config import get_db
from database.service import DatabaseService
from auth import get_current_user

router = APIRouter(prefix="/orders", tags=["order-rider"])


@router.get("/{order_id}/rider-deliveries", response_model=RiderDeliveryListResponse)
def get_order_rider_deliveries(
    order_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """주문에 대한 라이더 배송 신청 목록 조회 (구매자용)"""
    service = DatabaseService(db)
    
    # 주문이 해당 사용자의 것인지 확인
    order = service.get_order_with_details(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 라이더 배송 신청 목록 조회
    deliveries = service.get_order_rider_deliveries(order_id)
    
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


@router.put("/{order_id}/rider-delivery/{delivery_id}/accept", response_model=RiderDeliveryResponse)
def accept_rider_delivery(
    order_id: str,
    delivery_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """라이더 배송 신청 승락 (구매자용)"""
    service = DatabaseService(db)
    
    # 주문이 해당 사용자의 것인지 확인
    order = service.get_order_with_details(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 배송 신청이 해당 주문의 것인지 확인
    delivery = service.get_rider_delivery_by_id(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery request not found")
    
    if delivery.order_id != order_id:
        raise HTTPException(status_code=400, detail="Delivery request does not belong to this order")
    
    if delivery.status != "pending":
        raise HTTPException(status_code=400, detail="Delivery request is not pending")
    
    # 배송 신청 승락
    updated_delivery = service.update_delivery_status(delivery_id, "accepted")
    if not updated_delivery:
        raise HTTPException(status_code=500, detail="Failed to accept delivery request")
    
    # 주문 상태를 배송 중으로 변경
    order.status = "shipping"
    db.commit()
    
    # 라이더에게 배송 승락 알림 전송
    service.create_notification(
        user_id=updated_delivery.rider_id,
        title="배송 신청이 승락되었습니다!",
        message=f"주문 #{order_id[:8]}...의 배송 신청이 승락되었습니다. 배송을 시작해주세요.",
        type="delivery"
    )
    
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


@router.put("/{order_id}/rider-delivery/{delivery_id}/reject", response_model=RiderDeliveryResponse)
def reject_rider_delivery(
    order_id: str,
    delivery_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """라이더 배송 신청 거절 (구매자용)"""
    service = DatabaseService(db)
    
    # 주문이 해당 사용자의 것인지 확인
    order = service.get_order_with_details(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 배송 신청이 해당 주문의 것인지 확인
    delivery = service.get_rider_delivery_by_id(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery request not found")
    
    if delivery.order_id != order_id:
        raise HTTPException(status_code=400, detail="Delivery request does not belong to this order")
    
    if delivery.status != "pending":
        raise HTTPException(status_code=400, detail="Delivery request is not pending")
    
    # 배송 신청 거절
    updated_delivery = service.update_delivery_status(delivery_id, "rejected")
    if not updated_delivery:
        raise HTTPException(status_code=500, detail="Failed to reject delivery request")
    
    # 라이더에게 배송 거절 알림 전송
    service.create_notification(
        user_id=updated_delivery.rider_id,
        title="배송 신청이 거절되었습니다",
        message=f"주문 #{order_id[:8]}...의 배송 신청이 거절되었습니다.",
        type="delivery"
    )
    
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
