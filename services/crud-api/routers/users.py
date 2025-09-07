from fastapi import APIRouter, Depends
from models import User, Rider
from auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_my_info(current_user: dict = Depends(get_current_user)):
    # return appropriate schema including rider fields
    if current_user.get("role") == "rider":
        return Rider(**current_user)
    return User(**current_user)
