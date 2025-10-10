import uuid
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Product, ProductCreate
from database.config import get_db
from database.service import DatabaseService
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
    tags: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    service = DatabaseService(db)
    db_products = service.get_products(skip=(page - 1) * page_size, limit=page_size, 
                                     category_id=category_id, price_min=price_min, price_max=price_max, sort=sort)

    items: List[Product] = []
    for p in db_products:
        # Build Product model from DB row
        items.append(Product(
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
            created_at=p.created_at.isoformat() if p.created_at else datetime.utcnow().isoformat(),
        ))

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": len(items)  # Fast path; could implement count query if needed
    }


@router.post("", response_model=Product, status_code=201)
def create_product(
    request: ProductCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = DatabaseService(db)

    # Basic validation similar to tests' expectations
    if not request.title or request.price.amount < 0:
        raise HTTPException(status_code=422, detail="Invalid product data")
    
    # Validate category exists
    category = service.get_category_by_id(request.category_id)
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category")

    # Normalize location to Address-like dict if minimal fields provided
    raw_location = getattr(request.location, "model_dump", lambda: request.location)()
    if "postcode" not in raw_location:
        raw_location = {
            "postcode": raw_location.get("postal_code", ""),
            "line1": raw_location.get("line1") or raw_location.get("address", ""),
            "line2": raw_location.get("line2"),
            "city": raw_location.get("city", ""),
            "region": raw_location.get("region", ""),
            "country": raw_location.get("country", "KR")
        }

    # Create via service
    # Map uploaded images (from S3) using provided file ids if any
    image_entries = []
    for fid in (request.image_file_ids or []):
        # If fid is an S3 key, construct a public URL via base; otherwise accept absolute URL
        if fid.startswith("http://") or fid.startswith("https://"):
            image_entries.append({"file_id": fid, "url": fid})
        else:
            base = os.getenv("S3_PUBLIC_BASE_URL", "")
            url = f"{base}/{fid}" if base else fid
            image_entries.append({"file_id": fid, "url": url})

    created = service.create_product(
        title=request.title,
        description=request.description or "",
        price_amount=request.price.amount,
        category_id=request.category_id,
        seller_id=current_user["id"],
        location=raw_location,
        attributes=request.attributes or {},
        images=image_entries,
    )

    # Build API response
    return Product(
        id=created.id,
        title=created.title,
        description=created.description,
        price={"currency": created.price_currency, "amount": created.price_amount},
        images=created.images or [],
        category={"id": created.category_id, "name": created.category.name if created.category else "", "parent_id": created.category.parent_id if created.category else None},
        seller_id=created.seller_id,
        location=created.location or {},
        attributes=created.attributes or {},
        stock=created.stock or 1,
        is_featured=bool(created.is_featured),
        likes_count=created.likes_count or 0,
        created_at=created.created_at.isoformat() if created.created_at else datetime.utcnow().isoformat(),
    )


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: str, db: Session = Depends(get_db)):
    service = DatabaseService(db)
    p = service.get_product_by_id(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
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
        created_at=p.created_at.isoformat() if p.created_at else datetime.utcnow().isoformat(),
    )
