import pytest

BASE_URL = "http://localhost:8080/api/v1"
ADMIN_HEADERS = {"X-Roll-Number": "2024101096"}
VALID_HEADERS = {"X-Roll-Number": "2024101096", "X-User-ID": "1"}

@pytest.fixture
def base_url():
    return BASE_URL

@pytest.fixture
def valid_headers():
    return VALID_HEADERS

@pytest.fixture
def admin_headers():
    return ADMIN_HEADERS
