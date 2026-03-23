from conftest import assert_json_response, user_headers


USER_ID = 7


def _clear_cart(base_url):
    import requests

    resp = requests.delete(
        f"{base_url}/cart/clear",
        headers=user_headers(USER_ID),
        timeout=15,
    )
    assert_json_response(resp, 200)


def test_checkout_rejects_invalid_payment_method(base_url):
    import requests

    resp = requests.post(
        f"{base_url}/checkout",
        headers=user_headers(USER_ID),
        json={"payment_method": "UPI"},
        timeout=15,
    )
    assert_json_response(resp, 400)


def test_checkout_rejects_empty_cart(base_url):
    import requests

    _clear_cart(base_url)
    resp = requests.post(
        f"{base_url}/checkout",
        headers=user_headers(USER_ID),
        json={"payment_method": "CARD"},
        timeout=15,
    )
    assert_json_response(resp, 400)


def test_checkout_card_payment_status_paid(base_url):
    import requests

    _clear_cart(base_url)
    add = requests.post(
        f"{base_url}/cart/add",
        headers=user_headers(USER_ID),
        json={"product_id": 1, "quantity": 2},
        timeout=15,
    )
    assert_json_response(add, 200)

    checkout = requests.post(
        f"{base_url}/checkout",
        headers=user_headers(USER_ID),
        json={"payment_method": "CARD"},
        timeout=20,
    )
    body = assert_json_response(checkout, 200)
    assert body["payment_status"] == "PAID"
