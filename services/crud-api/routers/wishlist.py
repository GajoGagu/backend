from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Product, WishlistItemRequest, WishlistResponse
from database.config import get_db
from database.service import DatabaseService
from auth import get_current_user

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("", response_model=WishlistResponse)
def get_wishlist(
    current_user: dict = Depends(get_current_user),
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    service = DatabaseService(db)
    items = service.get_user_wishlist(current_user["id"]) or []

    # Pagination (simple slice)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = items[start:end]

    def to_api_product(p) -> Product:
        return Product(
            id=p.id,
            title=p.title,
            description=p.description,
            price={"currency": p.price_currency, "amount": p.price_amount},
            images=p.images or [],
            category={"id": p.category.id if p.category else p.category_id, "name": p.category.name if p.category else "", "parent_id": p.category.parent_id if p.category else None},
            seller_id=p.seller_id,
            location=p.location or {},
            attributes=p.attributes or {},
            stock=p.stock or 1,
            is_featured=bool(p.is_featured),
            likes_count=p.likes_count or 0,
            created_at=p.created_at.isoformat() if p.created_at else "",
        )

    return WishlistResponse(
        items=[
            {
                "product": to_api_product(w.product),
                "created_at": w.created_at.isoformat() if getattr(w, "created_at", None) else "",
            }
            for w in paginated if w.product is not None
        ],
        page=page,
        page_size=page_size,
        total=len(items)
    )


@router.post("/items", response_model=WishlistResponse)
def add_to_wishlist(
    request: WishlistItemRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = DatabaseService(db)
    product_id = request.product_id
    
    product = service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    service.add_to_wishlist(current_user["id"], product_id)
    return get_wishlist(current_user, db=db)


@router.delete("/items", response_model=WishlistResponse, status_code=200)
def remove_from_wishlist(
    request: WishlistItemRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = DatabaseService(db)
    product_id = request.product_id
    
    removed = service.remove_from_wishlist(current_user["id"], product_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Item not found in wishlist")
    return get_wishlist(current_user, db=db)
