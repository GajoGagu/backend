from pydantic import BaseModel, Field
from typing import Optional


class Money(BaseModel):
    currency: str = "KRW"
    amount: float


class Address(BaseModel):
    address: str  # 자유롭게 입력하는 주소
