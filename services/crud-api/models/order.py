from pydantic import BaseModel
from typing import List, Optional, Dict
from .base import Money, Address
from .product import Product


class OrderItem(BaseModel):
    product: Product
    quantity: int
    unit_price: Money
    line_total: Money


class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int
    price: float


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping_address: Address
    payment_method: str
    total_amount: float


class OrderStatusUpdate(BaseModel):
    status: str


class Order(BaseModel):
    id: str
    user_id: str
    status: str
    items: List[Dict]  # Simplified for now
    total_amount: float
    shipping_fee: float
    shipping_address: Dict
    payment_method: str
    created_at: str
    updated_at: str
