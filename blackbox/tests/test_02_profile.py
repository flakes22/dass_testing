from conftest import assert_json_response, user_headers


USER_ID = 8


def test_profile_requires_user_id_header(base_url):
    import requests

    resp = requests.get(
        f"{base_url}/profile",
        headers={"X-Roll-Number": "2024101096"},
        timeout=15,
    )
    assert_json_response(resp, 400)


def test_profile_update_rejects_short_name(base_url):
    import requests

    resp = requests.put(
        f"{base_url}/profile",
        headers=user_headers(USER_ID),
        json={"name": "A", "phone": "1234567890"},
        timeout=15,
    )
    assert_json_response(resp, 400)


def test_profile_update_rejects_non_digit_phone(base_url):
    import requests

    resp = requests.put(
        f"{base_url}/profile",
        headers=user_headers(USER_ID),
        json={"name": "Valid Name", "phone": "12345abcde"},
        timeout=15,
    )
    assert_json_response(resp, 400)


def test_profile_update_valid_boundary(base_url):
    import requests

    resp = requests.put(
        f"{base_url}/profile",
        headers=user_headers(USER_ID),
        json={"name": "AB", "phone": "9999999999"},
        timeout=15,
    )
    assert_json_response(resp, 200)
