from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserSignup(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    password: str = Field(min_length=12, max_length=72)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("full_name cannot be blank")
        return value

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    email: str
    full_name: str
    phone: Optional[str]
    created_at: datetime
    is_active: bool


class GarageCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1, max_length=255)
    spots_total: int = Field(gt=0, le=100000)

    @field_validator("name", "address")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value cannot be blank")
        return value


class GarageDetail(GarageCreate):
    model_config = ConfigDict(from_attributes=True)

    garage_id: str
    spots_available: int
    created_at: datetime


class ReservationCreate(BaseModel):
    garage_id: str = Field(min_length=3, max_length=100)
    license_plate: Optional[str] = Field(default=None, max_length=20)
    idempotency_key: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    @field_validator("garage_id", mode="before")
    @classmethod
    def normalize_garage_id(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("license_plate")
    @classmethod
    def normalize_license_plate(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip().upper()
        return value or None

    @field_validator("idempotency_key")
    @classmethod
    def normalize_idempotency_key(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None


class ReservationResponse(BaseModel):
    reservation_id: str
    status: str


class ReservationDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    garage_id: str
    license_plate: Optional[str]
    status: str
    idempotency_key: Optional[str]
    reserved_at: datetime
    released_at: Optional[datetime]
