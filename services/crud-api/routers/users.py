from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User, UpdateUserRequest, DeleteUserRequest
from auth import get_current_user
from database.config import get_db
from database.service import DatabaseService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_my_info(current_user: dict = Depends(get_current_user)):
    return User(**current_user)


@router.put("/me")
def update_my_info(
    request: UpdateUserRequest, 
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's information"""
    service = DatabaseService(db)
    
    # Update user information
    updated_user = service.update_user(
        user_id=current_user["id"],
        name=request.name,
        phone=request.phone,
        kakao_open_profile=request.kakao_open_profile,
        address=request.address
    )
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(
        id=updated_user.id,
        role=getattr(updated_user, "role", "user"),
        email=updated_user.email,
        name=updated_user.name,
        phone=updated_user.phone,
        address=updated_user.address,
        kakao_open_profile=updated_user.kakao_open_profile,
        created_at=updated_user.created_at.isoformat() if updated_user.created_at else None,
    )


@router.delete("/me")
def delete_my_account(
    request: DeleteUserRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user's account"""
    service = DatabaseService(db)
    
    # Verify password before deletion
    user = service.get_user_by_id(current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not service.verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Delete user account
    success = service.delete_user(current_user["id"])
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete account")
    
    return {"message": "Account deleted successfully"}
