import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(100), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    reservations = relationship(
        "Reservation",
        back_populates="user",
        passive_deletes=True,
    )


class Garage(Base):
    __tablename__ = "garages"

    garage_id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    spots_total = Column(Integer, nullable=False)
    spots_available = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    reservations = relationship(
        "Reservation",
        back_populates="garage",
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint(
            "spots_total > 0",
            name="check_spots_total_positive",
        ),
        CheckConstraint(
            "spots_available >= 0 AND spots_available <= spots_total",
            name="check_spots_available_bounds",
        ),
    )


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(100),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    garage_id = Column(
        String(100),
        ForeignKey("garages.garage_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    license_plate = Column(String(20), nullable=True)
    idempotency_key = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active", index=True)
    reserved_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    released_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="reservations")
    garage = relationship("Garage", back_populates="reservations")

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'released')",
            name="check_reservation_status",
        ),
        UniqueConstraint(
            "user_id",
            "idempotency_key",
            name="uq_reservation_user_idempotency",
        ),
    )
