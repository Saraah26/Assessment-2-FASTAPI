import argparse
import uuid

import requests

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
PASSWORD = "SecurePass123!"


def assert_status(response: requests.Response, expected: int, label: str) -> None:
    if response.status_code != expected:
        raise AssertionError(
            f"{label}: expected {expected}, got {response.status_code}. "
            f"Response: {response.text}"
        )
    print(f"PASS: {label} ({expected})")


def signup(base_url: str, email: str) -> str:
    response = requests.post(
        f"{base_url}/auth/signup",
        json={
            "email": email,
            "full_name": "Scenario Test Driver",
            "password": PASSWORD,
        },
        timeout=10,
    )
    assert_status(response, 201, "sign up")
    return response.json()["user_id"]


def signin(base_url: str, email: str, password: str) -> str:
    response = requests.post(
        f"{base_url}/auth/signin",
        json={"email": email, "password": password},
        timeout=10,
    )
    assert_status(response, 200, "sign in")
    return response.json()["access_token"]


def authorization(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()

    unique_number = str(uuid.uuid4().int)
    email = f"driver-{unique_number}@example.com"
    other_email = f"other-{unique_number}@example.com"

    assert_status(requests.get(f"{args.base_url}/"), 200, "root endpoint")
    assert_status(requests.get(f"{args.base_url}/health"), 200, "health endpoint")

    user_id = signup(args.base_url, email)

    duplicate_signup = requests.post(
        f"{args.base_url}/auth/signup",
        json={
            "email": email,
            "full_name": "Scenario Test Driver",
            "password": PASSWORD,
        },
        timeout=10,
    )
    assert_status(duplicate_signup, 409, "duplicate sign up")

    wrong_signin = requests.post(
        f"{args.base_url}/auth/signin",
        json={"email": email, "password": "WrongPassword123!"},
        timeout=10,
    )
    assert_status(wrong_signin, 401, "incorrect-password sign in")

    token = signin(args.base_url, email, PASSWORD)
    headers = authorization(token)

    assert_status(
        requests.get(f"{args.base_url}/users/me", timeout=10),
        401,
        "profile without token",
    )

    profile = requests.get(
        f"{args.base_url}/users/me",
        headers=headers,
        timeout=10,
    )
    assert_status(profile, 200, "own profile")

    own_user = requests.get(
        f"{args.base_url}/users/{user_id}",
        headers=headers,
        timeout=10,
    )
    assert_status(own_user, 200, "own profile by ID")

    other_profile = requests.get(
        f"{args.base_url}/users/DRIVER-000000000000",
        headers=headers,
        timeout=10,
    )
    assert_status(other_profile, 403, "other user's profile")

    garage_payload = {
        "name": "Scenario Garage",
        "address": "1 Test Street",
        "spots_total": 2,
    }

    unauthenticated_garage = requests.post(
        f"{args.base_url}/garages",
        json=garage_payload,
        timeout=10,
    )
    assert_status(
        unauthenticated_garage,
        401,
        "create garage without token",
    )

    created_garage = requests.post(
        f"{args.base_url}/garages",
        headers=headers,
        json=garage_payload,
        timeout=10,
    )
    assert_status(created_garage, 201, "create garage")
    garage_id = created_garage.json()["garage_id"]

    assert_status(
        requests.get(f"{args.base_url}/garages/{garage_id}", timeout=10),
        200,
        "get garage",
    )
    assert_status(
        requests.get(f"{args.base_url}/garages/UNKNOWN-999", timeout=10),
        404,
        "unknown garage",
    )
    assert_status(
        requests.get(f"{args.base_url}/garages", timeout=10),
        200,
        "list garages",
    )

    reservation_payload = {
        "garage_id": garage_id,
        "license_plate": "KA-01-AB-1234",
        "idempotency_key": f"reservation-{unique_number}",
    }

    unauthenticated_reservation = requests.post(
        f"{args.base_url}/reservations",
        json=reservation_payload,
        timeout=10,
    )
    assert_status(
        unauthenticated_reservation,
        401,
        "reservation without token",
    )

    reservation_response = requests.post(
        f"{args.base_url}/reservations",
        headers=headers,
        json=reservation_payload,
        timeout=10,
    )
    assert_status(reservation_response, 201, "create reservation")
    reservation_id = reservation_response.json()["reservation_id"]

    retry_response = requests.post(
        f"{args.base_url}/reservations",
        headers=headers,
        json=reservation_payload,
        timeout=10,
    )
    assert_status(retry_response, 200, "idempotent reservation retry")

    if retry_response.json()["reservation_id"] != reservation_id:
        raise AssertionError("Idempotent retry returned a different reservation")
    print("PASS: idempotent retry returned the original reservation")

    assert_status(
        requests.get(
            f"{args.base_url}/reservations",
            headers=headers,
            timeout=10,
        ),
        200,
        "list own reservations",
    )

    signup(args.base_url, other_email)
    other_token = signin(args.base_url, other_email, PASSWORD)

    forbidden_release = requests.post(
        f"{args.base_url}/reservations/{reservation_id}/release",
        headers=authorization(other_token),
        timeout=10,
    )
    assert_status(forbidden_release, 403, "release another user's reservation")

    release_response = requests.post(
        f"{args.base_url}/reservations/{reservation_id}/release",
        headers=headers,
        timeout=10,
    )
    assert_status(release_response, 200, "release own reservation")

    repeated_release = requests.post(
        f"{args.base_url}/reservations/{reservation_id}/release",
        headers=headers,
        timeout=10,
    )
    assert_status(repeated_release, 409, "release already-released reservation")

    print("\nAll endpoint and error-case scenarios passed.")


if __name__ == "__main__":
    main()
