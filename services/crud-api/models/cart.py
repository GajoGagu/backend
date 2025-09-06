from pydantic import BaseModel
from typing import List
from .base import Money
from .product import Product


class CartItem(BaseModel):
    item_id: str
    product: Product
    quantity: int
    unit_price: Money
    line_total: Money


class Cart(BaseModel):
    items: List[CartItem] = []
    subtotal: Money
    shipping_fee: Money
    discount_total: Money = Money(currency="KRW", amount=0)
    grand_total: Money


class ShippingQuote(BaseModel):
    method: str = "standard"
    fee: Money
    estimated_days: int = 3
