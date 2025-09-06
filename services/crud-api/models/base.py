from pydantic import BaseModel, Field
from typing import Optional


class Money(BaseModel):
    currency: str = "KRW"
    amount: float


class Address(BaseModel):
    postcode: str
    line1: str
    line2: Optional[str] = None
    city: str
    region: str
    country: str = "KR"
