from pydantic import BaseModel
from typing import List, Optional, Dict
from .base import Money, Address
from .product import Product


class OrderItem(BaseModel):
    product: Product
    quantity: int
    unit_price: Money
    line_total: Money


class Order(BaseModel):
    id: str
    status: str
    items: List[OrderItem]
    address: Address
    shipping_fee: Money
    subtotal: Money
    discount_total: Money = Money(currency="KRW", amount=0)
    total: Money
    payment_method: str
    assigned_rider: Optional[Dict] = None
    created_at: str
