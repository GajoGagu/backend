from pydantic import BaseModel
from typing import Optional, List
from .base import Address, Money
from .auth import User


class RiderDeliveryRequest(BaseModel):
    """라이더 배송 신청 요청"""
    order_id: str
    delivery_fee: float


class RiderDeliveryResponse(BaseModel):
    """라이더 배송 신청 응답"""
    id: str
    order_id: str
    rider_id: str
    delivery_fee: float
    status: str
    seller_info: User  # 판매자 정보
    buyer_info: User   # 구매자 정보
    created_at: str
    updated_at: Optional[str] = None


class OrderWithDetails(BaseModel):
    """배송 가능한 주문 상세 정보"""
    order_id: str
    buyer_info: User  # 구매자 정보
    seller_info: User  # 판매자 정보
    product_info: dict  # 상품 정보
    total_amount: float
    created_at: str


class DeliveryStatusUpdate(BaseModel):
    """배송 상태 업데이트 요청"""
    status: str  # accepted, rejected, in_progress, completed


class RiderDeliveryListResponse(BaseModel):
    """라이더 배송 목록 응답"""
    items: List[RiderDeliveryResponse]
    total: int
