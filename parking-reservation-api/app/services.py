from datetime import datetime, timezone
import secrets
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password
from app.models import Garage, Reservation, User
from app.schemas import GarageCreate, UserSignup


class ServiceError(Exception):
    status_code = 400

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(ServiceError):
    status_code = 404


class ConflictError(ServiceError):
    status_code = 409


class ForbiddenError(ServiceError):
    status_code = 403


def create_user(db: Session, user_data: UserSignup) -> User:
    user = User(
        user_id=f"DRIVER-{secrets.randbelow(10**12):012d}",
        email=str(user_data.email),
        full_name=user_data.full_name,
        phone=user_data.phone,
        password_hash=hash_password(user_data.password),
        is_active=True,
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError(
            "A user with this ID or email already exists"
        ) from error

    db.refresh(user)
    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> Optional[User]:
    user = db.scalar(select(User).where(User.email == email.lower()))

    if user is None or not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def get_user(db: Session, user_id: str) -> Optional[User]:
    return db.get(User, user_id)


def create_garage(db: Session, garage_data: GarageCreate) -> Garage:
    garage = Garage(
        garage_id=f"GARAGE-{secrets.randbelow(10**12):012d}",
        name=garage_data.name,
        address=garage_data.address,
        spots_total=garage_data.spots_total,
        spots_available=garage_data.spots_total,
    )

    db.add(garage)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError("Could not create garage") from error

    db.refresh(garage)
    return garage


def get_garage(db: Session, garage_id: str) -> Optional[Garage]:
    return db.get(Garage, garage_id)


def list_garages(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Garage]:
    return list(
        db.scalars(
            select(Garage)
            .order_by(Garage.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
    )


def create_reservation(
    db: Session,
    user_id: str,
    garage_id: str,
    license_plate: Optional[str] = None,
    idempotency_key: Optional[str] = None,
) -> tuple[Reservation, bool]:
    """
    Reserve one spot atomically.

    The Boolean result is True for a newly-created reservation and False
    when the request is an idempotent retry of an existing reservation.
    """
    if idempotency_key:
        existing_reservation = db.scalar(
            select(Reservation).where(
                Reservation.user_id == user_id,
                Reservation.idempotency_key == idempotency_key,
            )
        )
        if existing_reservation is not None:
            return existing_reservation, False

    garage_exists = db.get(Garage, garage_id)
    if garage_exists is None:
        raise NotFoundError(f"Garage {garage_id} not found")

    # This single SQL statement prevents concurrent requests from reserving
    # more spots than are available.
    allocated_garage_id = db.scalar(
        update(Garage)
        .where(
            Garage.garage_id == garage_id,
            Garage.spots_available > 0,
        )
        .values(spots_available=Garage.spots_available - 1)
        .returning(Garage.garage_id)
    )

    if allocated_garage_id is None:
        db.rollback()
        raise ConflictError(f"No available spots in {garage_id}")

    reservation = Reservation(
        user_id=user_id,
        garage_id=garage_id,
        license_plate=license_plate,
        idempotency_key=idempotency_key,
        status="active",
    )
    db.add(reservation)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()

        # A matching unique-key error can occur when two identical requests
        # arrive at nearly the same time. Return the already-created result.
        if idempotency_key:
            existing_reservation = db.scalar(
                select(Reservation).where(
                    Reservation.user_id == user_id,
                    Reservation.idempotency_key == idempotency_key,
                )
            )
            if existing_reservation is not None:
                return existing_reservation, False

        raise ConflictError("Could not create reservation") from error

    db.refresh(reservation)
    return reservation, True


def get_reservations_by_user(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 100,
) -> list[Reservation]:
    return list(
        db.scalars(
            select(Reservation)
            .where(Reservation.user_id == user_id)
            .order_by(Reservation.reserved_at.desc())
            .offset(skip)
            .limit(limit)
        )
    )


def release_spot(
    db: Session,
    reservation_id: str,
    user_id: str,
) -> Reservation:
    reservation = db.scalar(
        select(Reservation)
        .where(Reservation.id == reservation_id)
        .with_for_update()
    )

    if reservation is None:
        raise NotFoundError(f"Reservation {reservation_id} not found")

    if reservation.user_id != user_id:
        raise ForbiddenError("You cannot release another driver's reservation")

    if reservation.status != "active":
        raise ConflictError(f"Reservation {reservation_id} was already released")

    garage = db.scalar(
        select(Garage)
        .where(Garage.garage_id == reservation.garage_id)
        .with_for_update()
    )

    if garage is None:
        raise NotFoundError(f"Garage {reservation.garage_id} not found")

    garage.spots_available += 1
    reservation.status = "released"
    reservation.released_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ConflictError("Could not release reservation") from error

    db.refresh(reservation)
    return reservation
