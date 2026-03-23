from conftest import assert_json_response, user_headers


USER_ID = 2


def _clear_cart(base_url):
    import requests

    resp = requests.delete(
        f"{base_url}/cart/clear",
        headers=user_headers(USER_ID),
        timeout=15,
    )
    assert_json_response(resp, 200)


def _add_item(base_url, product_id, quantity):
    import requests

    resp = requests.post(
        f"{base_url}/cart/add",
        headers=user_headers(USER_ID),
        json={"product_id": product_id, "quantity": quantity},
        timeout=15,
    )
    assert_json_response(resp, 200)


def test_coupon_expired_rejected(base_url):
    import requests

    _clear_cart(base_url)
    _add_item(base_url, 5, 4)
    resp = requests.post(
        f"{base_url}/coupon/apply",
        headers=user_headers(USER_ID),
        json={"coupon_code": "EXPIRED100"},
        timeout=15,
    )
    assert_json_response(resp, 400)


def test_coupon_fixed_discount_applies_correctly(base_url):
    import requests

    _clear_cart(base_url)
    _add_item(base_url, 5, 4)
    resp = requests.post(
        f"{base_url}/coupon/apply",
        headers=user_headers(USER_ID),
        json={"coupon_code": "BONUS75"},
        timeout=15,
    )
    body = assert_json_response(resp, 200)
    assert body["discount"] == 75
    assert body["new_total"] == 925


def test_coupon_percent_discount_must_use_percentage(base_url):
    import requests

    _clear_cart(base_url)
    _add_item(base_url, 5, 4)
    resp = requests.post(
        f"{base_url}/coupon/apply",
        headers=user_headers(USER_ID),
        json={"coupon_code": "FIRSTORDER"},
        timeout=15,
    )
    body = assert_json_response(resp, 200)
    assert body["discount"] == 150
    assert body["new_total"] == 850
