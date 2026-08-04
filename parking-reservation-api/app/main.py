from fastapi import FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db import engine, init_db
from app.routes_auth import router as auth_router
from app.routes_garages import router as garages_router
from app.routes_reservations import router as reservations_router
from app.routes_users import router as users_router

app = FastAPI(
    title="Parking Garage Reservation API",
    version="1.0.0",
)


@app.on_event("startup")
def startup() -> None:
    init_db()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(garages_router)
app.include_router(reservations_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Parking Garage Reservation API is running"}


@app.get("/health")
def health() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from error

    return {"status": "healthy"}