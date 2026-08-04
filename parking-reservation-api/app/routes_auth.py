from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token
from app.db import get_db
from app.schemas import SignInRequest, TokenResponse, UserDetail, UserSignup
from app.services import ConflictError, authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db),
) -> UserDetail:
    try:
        return create_user(db, user_data)
    except ConflictError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from error


@router.post("/signin", response_model=TokenResponse)
def signin(
    credentials: SignInRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = authenticate_user(
        db=db,
        email=str(credentials.email),
        password=credentials.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return TokenResponse(
        access_token=create_access_token(user.user_id),
    )