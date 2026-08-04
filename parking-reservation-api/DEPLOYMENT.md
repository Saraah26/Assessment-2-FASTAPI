# Parking Garage Reservation API - Deployment Guide

## Prerequisites
- Python 3.11+, Docker, pip, Git

## 1. Clone
```bash
git clone <repository-url>
cd parking-reservation-api
```

## 2. PostgreSQL
```bash
docker run --name parking_pg \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=parkingdb \
  -p 5432:5432 -d postgres:16
```
```bash
docker ps | grep parking_pg
docker stop parking_pg && docker rm parking_pg   # fresh start
```

## 3. Virtual environment
```bash
python3.11 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

## 4. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure (optional)
```bash
# .env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/parkingdb
```

## 6. Run
```bash
uvicorn app.main:app --reload --port 8000
```

## 7. Verify
```bash
curl http://localhost:8000/health
```
Swagger UI: http://localhost:8000/docs

## 8. Seed data (optional)
```bash
python scripts/seed_data.py --all
```

## Testing Guide

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"user_id": "DRIVER-001", "email": "driver@example.com", "full_name": "Vikram Rao"}'

curl -X POST http://localhost:8000/garages \
  -H "Content-Type: application/json" \
  -d '{"garage_id": "GARAGE-001", "name": "Downtown Parking Garage", "address": "12 Market Street", "spots_total": 200}'

curl -X POST http://localhost:8000/reservations \
  -H "Content-Type: application/json" \
  -d '{"user_id": "DRIVER-001", "garage_id": "GARAGE-001", "idempotency_key": "test-1"}'

curl -X POST http://localhost:8000/reservations/{reservation_id}/release
```
