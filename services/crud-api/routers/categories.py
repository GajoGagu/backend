from typing import List
from fastapi import APIRouter, Depends
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
