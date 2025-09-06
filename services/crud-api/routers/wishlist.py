from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from models import Product
from database import wishlist_db, products_db
from auth import get_current_user

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("", response_model=Dict[str, Any])
def get_wishlist(
    current_user: dict = Depends(get_current_user),
    page: int = 1,
    page_size: int = 20
):
    user_id = current_user["id"]
    wishlist_product_ids = wishlist_db.get(user_id, [])
    
    products = [products_db[pid] for pid in wishlist_product_ids if pid in products_db]
    
    start = (page - 1) * page_size
    end = start + page_size
    paginated_products = products[start:end]
    
    return {
        "items": [Product(**p) for p in paginated_products],
        "page": page,
        "page_size": page_size,
        "total": len(products)
    }


@router.put("/{product_id}", status_code=204)
def add_to_wishlist(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    user_id = current_user["id"]
    if user_id not in wishlist_db:
        wishlist_db[user_id] = []
    
    if product_id not in wishlist_db[user_id]:
        wishlist_db[user_id].append(product_id)
        products_db[product_id]["likes_count"] += 1


@router.delete("/{product_id}", status_code=204)
def remove_from_wishlist(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    if user_id in wishlist_db and product_id in wishlist_db[user_id]:
        wishlist_db[user_id].remove(product_id)
        if product_id in products_db:
            products_db[product_id]["likes_count"] = max(0, products_db[product_id]["likes_count"] - 1)
