from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import services
from app.auth import get_current_user
from app.db import get_db
from app.models import User
from app.schemas import GarageCreate, GarageDetail
from app.services import ServiceError

router = APIRouter(prefix="/garages", tags=["garages"])

PaginationSkip = Annotated[int, Query(ge=0)]
PaginationLimit = Annotated[int, Query(ge=1, le=100)]


@router.post("", response_model=GarageDetail, status_code=status.HTTP_201_CREATED)
def create_garage(
    garage: GarageCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> GarageDetail:
    try:
        return services.create_garage(db, garage)
    except ServiceError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from error


@router.get("/{garage_id}", response_model=GarageDetail)
def get_garage(
    garage_id: str,
    db: Session = Depends(get_db),
) -> GarageDetail:
    garage = services.get_garage(db, garage_id)

    if garage is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garage not found",
        )

    return garage


@router.get("", response_model=list[GarageDetail])
def list_garages(
    db: Session = Depends(get_db),
    skip: PaginationSkip = 0,
    limit: PaginationLimit = 100,
) -> list[GarageDetail]:
    return services.list_garages(db, skip=skip, limit=limit)