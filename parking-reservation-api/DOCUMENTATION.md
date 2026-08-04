# Parking Garage Reservation API - Technical Documentation

## Project Overview

A FastAPI backend for garage parking: drivers register, garages register
with a fixed spot capacity, and drivers reserve / release a spot.

### Tech Stack
FastAPI 0.109.0, PostgreSQL 16, SQLAlchemy 2.0.25, Pydantic v2, Uvicorn,
Python 3.11+.

## Architecture

```
parking-reservation-api/
├── app/
│   ├── main.py                  # App entry point, router registration
│   ├── config.py                # Environment configuration
│   ├── db.py                    # DB connection/session management
│   ├── models.py                # SQLAlchemy models (User, Garage, Reservation)
│   ├── schemas.py                # Pydantic request/response models
│   ├── services.py               # Business logic layer
│   ├── routes_users.py           # Driver endpoints
│   ├── routes_garages.py         # Garage endpoints
│   ├── routes_reservations.py    # Reserve / release endpoints
│   └── auth.py                   # Authentication framework (extensible)
```

```
API Layer (routes_*.py) → Business Logic (services.py) → ORM (models.py) → PostgreSQL
```

## Database Schema

### `users`
user_id (PK), email (unique), full_name, phone, created_at, is_active

### `garages`
garage_id (PK), name, address, spots_total (CHECK >= 0), spots_available
(CHECK >= 0), created_at

### `reservations`
id (PK, UUID string), user_id (FK), garage_id (FK), license_plate,
idempotency_key, status (`active` / `released`), reserved_at, released_at

Relationships: User 1—N Reservations, Garage 1—N Reservations. CASCADE
DELETE on both FKs.

## API Flows

### Reserve
```
POST /reservations
  → services.create_reservation()
      - optional idempotency lookup
      - validate spots_available > 0
      - decrement spots_available, insert reservation row
      - gate-control "sync window" delay
  → { reservation_id, status }
```

### Release
```
POST /reservations/{reservation_id}/release
  → services.release_spot()
      - validate reservation is still active
      - increment spots_available
      - mark reservation released
  → reservation detail
```

## Local Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md).

## Testing Guide
See README/DEPLOYMENT for curl examples. `scripts/run_scenarios.py`
exercises reservation retries, concurrent reservations against a small
garage, and invalid-input handling.

## Development Guidelines
- Keep business logic in `services.py`; routes stay thin.
- New endpoints get Pydantic validation.
- Mutating endpoints a client might retry should be idempotent.
