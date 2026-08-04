from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import services
from app.auth import get_current_user
from app.db import get_db
from app.models import User
from app.schemas import (
    ReservationCreate,
    ReservationDetail,
    ReservationResponse,
)
from app.services import ServiceError

router = APIRouter(prefix="/reservations", tags=["reservations"])

PaginationSkip = Annotated[int, Query(ge=0)]
PaginationLimit = Annotated[int, Query(ge=1, le=100)]


@router.post(
    "",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reservation(
    reservation_data: ReservationCreate,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReservationResponse:
    try:
        reservation, created = services.create_reservation(
            db=db,
            user_id=current_user.user_id,
            garage_id=reservation_data.garage_id,
            license_plate=reservation_data.license_plate,
            idempotency_key=reservation_data.idempotency_key,
        )
    except ServiceError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from error

    if not created:
        response.status_code = status.HTTP_200_OK

    return ReservationResponse(
        reservation_id=reservation.id,
        status=reservation.status,
    )


@router.get("", response_model=list[ReservationDetail])
def list_my_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: PaginationSkip = 0,
    limit: PaginationLimit = 100,
) -> list[ReservationDetail]:
    return services.get_reservations_by_user(
        db=db,
        user_id=current_user.user_id,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/{reservation_id}/release",
    response_model=ReservationDetail,
)
def release_reservation(
    reservation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReservationDetail:
    try:
        return services.release_spot(
            db=db,
            reservation_id=reservation_id,
            user_id=current_user.user_id,
        )
    except ServiceError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from error