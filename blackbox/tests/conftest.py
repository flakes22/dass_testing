import os
from typing import Any

import pytest
import requests


BASE_URL = os.getenv("QUICKCART_BASE_URL", "http://localhost:8080/api/v1")
ROLL_NUMBER = os.getenv("QUICKCART_ROLL", "2024101096")


@pytest.fixture(scope="session")
def api() -> requests.Session:
    s = requests.Session()
    s.headers.update({"X-Roll-Number": ROLL_NUMBER})
    return s


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


def user_headers(user_id: int) -> dict[str, str]:
    return {
        "X-Roll-Number": ROLL_NUMBER,
        "X-User-ID": str(user_id),
    }


def assert_json_response(resp: requests.Response, expected_status: int) -> Any:
    assert resp.status_code == expected_status, resp.text
    return resp.json()
