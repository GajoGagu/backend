from fastapi import APIRouter, Depends
from models import User
from auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_my_info(current_user: dict = Depends(get_current_user)):
    return User(**current_user)
