from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class FurnitureCategory(str, Enum):
    """가구 카테고리 열거형"""
    BED = "bed"
    CHAIR = "chair"
    DRESSER = "dresser"
    LAMP = "lamp"
    SOFA = "sofa"
    TABLE = "table"

class DetectionItem(BaseModel):
    """탐지된 가구 객체 정보"""
    category: str
    confidence: float
    bbox: List[float]  # [x_min, y_min, x_max, y_max]
    cropped_image_path: Optional[str] = None

class DetectionResponse(BaseModel):
    """객체 탐지 API 응답"""
    success: bool
    message: str
    detections: List[DetectionItem]
    total_count: int

class FurnitureItem(BaseModel):
    """가구 제품 정보"""
    id: str
    name: str
    category: str
    price: float
    image_url: str
    product_url: str
    similarity_score: float
    style_features: Optional[List[float]] = None

class SimilarityResponse(BaseModel):
    """유사도 기반 추천 API 응답"""
    success: bool
    message: str
    recommendations: List[FurnitureItem]
    total_count: int

class ErrorResponse(BaseModel):
    """에러 응답"""
    success: bool = False
    error: str
    detail: Optional[str] = None
