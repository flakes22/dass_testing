from conftest import assert_json_response, user_headers


USER_ID = 10


def test_loyalty_get_structure(base_url):
    import requests

    resp = requests.get(
        f"{base_url}/loyalty",
        headers=user_headers(USER_ID),
        timeout=15,
    )
    body = assert_json_response(resp, 200)
    assert "loyalty_points" in body


def test_loyalty_redeem_minimum_points_boundary(base_url):
    import requests

    resp = requests.post(
        f"{base_url}/loyalty/redeem",
        headers=user_headers(USER_ID),
        json={"points": 0},
        timeout=15,
    )
    assert_json_response(resp, 400)
