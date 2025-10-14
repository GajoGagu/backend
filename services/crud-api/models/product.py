from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from .base import Money, Address


class SellerInfo(BaseModel):
    """판매자 공개 정보"""
    name: str
    address: str  # 단순한 문자열 주소
    kakao_open_profile: str


class Category(BaseModel):
    id: str
    name: str
    parent_id: Optional[str] = None


class Image(BaseModel):
    file_id: str
    url: str
    width: Optional[int] = None
    height: Optional[int] = None


class Product(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: Money
    images: List[Image] = []
    category: Category
    seller_id: Optional[str] = None
    seller_info: Optional[SellerInfo] = None  # 판매자 공개 정보
    location: str  # 단순한 문자열 주소
    attributes: Dict[str, Any] = {}
    stock: int = 1
    is_featured: bool = False
    likes_count: int = 0
    created_at: str


class ProductCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: Money
    category_id: str
    location: str  # 단순한 문자열 주소
    attributes: Dict[str, Any] = {}
    image_file_ids: List[str] = []


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Money] = None
    category_id: Optional[str] = None
    location: Optional[str] = None  # 단순한 문자열 주소
    attributes: Optional[Dict[str, Any]] = None
    image_file_ids: Optional[List[str]] = None
    stock: Optional[int] = None
    is_featured: Optional[bool] = None


class WishlistItemRequest(BaseModel):
    product_id: str


class WishlistItem(BaseModel):
    product: Product
    created_at: str


class WishlistResponse(BaseModel):
    items: List[WishlistItem]
    page: int
    page_size: int
    total: int