from conftest import assert_json_response


def test_admin_users_missing_roll_header_returns_401(base_url):
    import requests

    resp = requests.get(f"{base_url}/admin/users", timeout=15)
    body = assert_json_response(resp, 401)
    assert "error" in body


def test_admin_users_invalid_roll_header_returns_400(base_url):
    import requests

    resp = requests.get(
        f"{base_url}/admin/users",
        headers={"X-Roll-Number": "abc"},
        timeout=15,
    )
    body = assert_json_response(resp, 400)
    assert "error" in body


def test_admin_users_success_structure(api, base_url):
    resp = api.get(f"{base_url}/admin/users", timeout=20)
    body = assert_json_response(resp, 200)
    assert isinstance(body, list)
    assert len(body) > 0
    first = body[0]
    for key in ["user_id", "name", "email", "phone", "wallet_balance", "loyalty_points"]:
        assert key in first
