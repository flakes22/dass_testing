from conftest import assert_json_response, user_headers


USER_ID = 2
PRODUCT_ID = 1


def _clear_cart(base_url):
    import requests

    resp = requests.delete(
        f"{base_url}/cart/clear",
        headers=user_headers(USER_ID),
        timeout=15,
    )
    assert_json_response(resp, 200)


def test_cart_add_quantity_zero_must_be_rejected(base_url):
    import requests

    _clear_cart(base_url)
    resp = requests.post(
        f"{base_url}/cart/add",
        headers=user_headers(USER_ID),
        json={"product_id": PRODUCT_ID, "quantity": 0},
        timeout=15,
    )
    assert resp.status_code == 400, resp.text


def test_cart_add_negative_quantity_rejected(base_url):
    import requests

    resp = requests.post(
        f"{base_url}/cart/add",
        headers=user_headers(USER_ID),
        json={"product_id": PRODUCT_ID, "quantity": -1},
        timeout=15,
    )
    assert_json_response(resp, 400)


def test_cart_add_missing_product_404(base_url):
    import requests

    resp = requests.post(
        f"{base_url}/cart/add",
        headers=user_headers(USER_ID),
        json={"product_id": 999999, "quantity": 1},
        timeout=15,
    )
    assert_json_response(resp, 404)


def test_cart_subtotal_and_total_must_match_quantity_times_price(base_url):
    import requests

    _clear_cart(base_url)
    add = requests.post(
        f"{base_url}/cart/add",
        headers=user_headers(USER_ID),
        json={"product_id": PRODUCT_ID, "quantity": 3},
        timeout=15,
    )
    assert_json_response(add, 200)

    cart_resp = requests.get(
        f"{base_url}/cart",
        headers=user_headers(USER_ID),
        timeout=15,
    )
    cart = assert_json_response(cart_resp, 200)
    assert len(cart["items"]) >= 1

    item = next(i for i in cart["items"] if i["product_id"] == PRODUCT_ID)
    expected_subtotal = item["quantity"] * item["unit_price"]
    assert item["subtotal"] == expected_subtotal

    expected_total = sum(i["subtotal"] for i in cart["items"])
    assert cart["total"] == expected_total
