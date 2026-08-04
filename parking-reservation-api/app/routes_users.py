from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.models import User
from app.schemas import UserDetail

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDetail)
def get_my_profile(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


@router.get("/{user_id}", response_model=UserDetail)
def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
) -> User:
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile",
        )

    return current_user