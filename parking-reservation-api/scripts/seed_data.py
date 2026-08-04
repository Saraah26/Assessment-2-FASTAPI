import argparse
import uuid

import requests

DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def ensure_user(
    base_url: str,
    email: str,
    full_name: str,
    password: str,
) -> str:
    signup_response = requests.post(
        f"{base_url}/auth/signup",
        json={
            "email": email,
            "full_name": full_name,
            "password": password,
        },
        timeout=10,
    )

    if signup_response.status_code == 201:
        print(f"Created user: {signup_response.json()['user_id']}")
    elif signup_response.status_code == 409:
        print(f"User already exists: {email}")
    else:
        signup_response.raise_for_status()

    signin_response = requests.post(
        f"{base_url}/auth/signin",
        json={"email": email, "password": password},
        timeout=10,
    )
    signin_response.raise_for_status()

    return signin_response.json()["access_token"]


def ensure_garage(
    base_url: str,
    token: str,
) -> str:
    response = requests.post(
        f"{base_url}/garages",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Downtown Parking Garage",
            "address": "12 Market Street",
            "spots_total": 200,
        },
        timeout=10,
    )

    response.raise_for_status()
    garage_id = response.json()["garage_id"]
    print(f"Created garage: {garage_id}")
    return garage_id


def create_reservation(
    base_url: str,
    token: str,
    garage_id: str,
    idempotency_key: str,
) -> None:
    response = requests.post(
        f"{base_url}/reservations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "garage_id": garage_id,
            "license_plate": "KA-01-AB-1234",
            "idempotency_key": idempotency_key,
        },
        timeout=10,
    )
    response.raise_for_status()

    reservation = response.json()
    print(
        f"Reservation {reservation['reservation_id']}: "
        f"{reservation['status']}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()

    token = ensure_user(
        base_url=args.base_url,
        email="driver1@example.com",
        full_name="Vikram Rao",
        password="SecurePass123!",
    )
    garage_id = ensure_garage(args.base_url, token)
    create_reservation(
        args.base_url,
        token,
        garage_id,
        f"seed-reservation-{uuid.uuid4().hex}",
    )


if __name__ == "__main__":
    main()
