from pydantic import BaseModel
from typing import List, Dict, Any
from .product import Product


class AIStyleMatchRequest(BaseModel):
    room_image_id: str
    furniture_image_ids: List[str] = []
    top_k: int = 20
    filters: Dict[str, Any] = {}


class AIMatch(BaseModel):
    product: Product
    score: float


class AIStyleMatchResult(BaseModel):
    matches: List[AIMatch]
    generated_at: str
