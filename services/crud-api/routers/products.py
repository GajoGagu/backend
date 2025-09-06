import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends
from models import Product, ProductCreate
from database import products_db, categories_db
from auth import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=Dict[str, Any])
def get_products(
    q: Optional[str] = None,
    category_id: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    sort: str = "recent",
    page: int = 1,
    page_size: int = 20,
    tags: Optional[List[str]] = None
):
    products = list(products_db.values())
    
    # Apply filters
    if q:
        products = [p for p in products if q.lower() in p["title"].lower()]
    if category_id:
        products = [p for p in products if p["category"]["id"] == category_id]
    if price_min:
        products = [p for p in products if p["price"]["amount"] >= price_min]
    if price_max:
        products = [p for p in products if p["price"]["amount"] <= price_max]
    
    # Apply sorting
    if sort == "price_asc":
        products.sort(key=lambda x: x["price"]["amount"])
    elif sort == "price_desc":
        products.sort(key=lambda x: x["price"]["amount"], reverse=True)
    elif sort == "popular":
        products.sort(key=lambda x: x["likes_count"], reverse=True)
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated_products = products[start:end]
    
    return {
        "items": [Product(**p) for p in paginated_products],
        "page": page,
        "page_size": page_size,
        "total": len(products)
    }


@router.post("", response_model=Product, status_code=201)
def create_product(
    request: ProductCreate,
    current_user: dict = Depends(get_current_user)
):
    if request.category_id not in categories_db:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    product_id = str(uuid.uuid4())
    product = {
        "id": product_id,
        "title": request.title,
        "description": request.description,
        "price": request.price.dict(),
        "images": [],
        "category": categories_db[request.category_id],
        "seller_id": current_user["id"],
        "location": request.location.dict(),
        "attributes": request.attributes,
        "stock": 1,
        "is_featured": False,
        "likes_count": 0,
        "created_at": datetime.now().isoformat()
    }
    
    products_db[product_id] = product
    return Product(**product)


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: str):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**products_db[product_id])
