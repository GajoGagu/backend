from typing import List
from fastapi import APIRouter
from ..models import Category
from ..database import categories_db

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[Category])
def get_categories():
    return [Category(**cat) for cat in categories_db.values()]
