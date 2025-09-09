from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Category
from database.config import get_db
from database.service import DatabaseService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[Category])
def get_categories(db: Session = Depends(get_db)):
    service = DatabaseService(db)
    categories = service.get_categories()
    return [
        Category(id=c.id, name=c.name, parent_id=c.parent_id) for c in categories
    ]


@router.get("/{category_id}", response_model=Category)
def get_category_detail(category_id: str, db: Session = Depends(get_db)):
    """Get a specific category by ID"""
    service = DatabaseService(db)
    category = service.get_category_by_id(category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return Category(id=category.id, name=category.name, parent_id=category.parent_id)