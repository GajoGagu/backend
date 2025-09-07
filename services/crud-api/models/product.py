from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from .base import Money, Address


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
    seller_id: str
    location: Address
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
    location: Dict[str, Any]
    attributes: Dict[str, Any] = {}
    image_file_ids: List[str] = []
