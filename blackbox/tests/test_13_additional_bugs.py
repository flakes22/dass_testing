import requests

from conftest import assert_json_response, user_headers


def _clear_cart(base_url: str, user_id: int) -> None:
    resp = requests.delete(
        f"{base_url}/cart/clear",
        headers=user_headers(user_id),
        timeout=15,
    )
    assert_json_response(resp, 200)


def test_profile_nonexistent_user_header_should_be_400(base_url):
    resp = requests.get(
        f"{base_url}/profile",
        headers=user_headers(999999),
        timeout=15,
    )
    assert resp.status_code == 400, resp.text


def test_address_pincode_non_digit_should_be_rejected(base_url):
    resp = requests.post(
        f"{base_url}/addresses",
        headers=user_headers(5),
        json={
            "label": "HOME",
            "street": "12345 Main Street",
            "city": "Hyd",
            "pincode": "ABCDE1",
            "is_default": False,
        },
        timeout=15,
    )
    assert resp.status_code == 400, resp.text


def test_cart_update_non_existing_product_should_404(base_url):
    _clear_cart(base_url, 2)
    resp = requests.post(
        f"{base_url}/cart/update",
        headers=user_headers(2),
        json={"product_id": 999999, "quantity": 1},
        timeout=15,
    )
    assert resp.status_code == 404, resp.text


def test_cart_subtotal_exact_after_update_quantity(base_url):
    _clear_cart(base_url, 2)
    add = requests.post(
        f"{base_url}/cart/add",
        headers=user_headers(2),
        json={"product_id": 1, "quantity": 1},
        timeout=15,
    )
    assert_json_response(add, 200)

    upd = requests.post(
        f"{base_url}/cart/update",
        headers=user_headers(2),
        json={"product_id": 1, "quantity": 4},
        timeout=15,
    )
    assert_json_response(upd, 200)

    cart = assert_json_response(
        requests.get(f"{base_url}/cart", headers=user_headers(2), timeout=15),
        200,
    )
    item = next(i for i in cart["items"] if i["product_id"] == 1)
    assert item["subtotal"] == item["quantity"] * item["unit_price"]


def test_cart_total_single_item_must_equal_subtotal(base_url):
    _clear_cart(base_url, 2)
    assert_json_response(
        requests.post(
            f"{base_url}/cart/add",
            headers=user_headers(2),
            json={"product_id": 2, "quantity": 2},
            timeout=15,
        ),
        200,
    )
    cart = assert_json_response(
        requests.get(f"{base_url}/cart", headers=user_headers(2), timeout=15),
        200,
    )
    assert len(cart["items"]) == 1
    assert cart["total"] == cart["items"][0]["subtotal"]


def test_cart_total_multiple_items_must_include_last_item(base_url):
    _clear_cart(base_url, 2)
    assert_json_response(
        requests.post(
            f"{base_url}/cart/add",
            headers=user_headers(2),
            json={"product_id": 1, "quantity": 2},
            timeout=15,
        ),
        200,
    )
    assert_json_response(
        requests.post(
            f"{base_url}/cart/add",
            headers=user_headers(2),
            json={"product_id": 2, "quantity": 2},
            timeout=15,
        ),
        200,
    )
    cart = assert_json_response(
        requests.get(f"{base_url}/cart", headers=user_headers(2), timeout=15),
        200,
    )
    assert len(cart["items"]) >= 2
    expected_total = sum(i["subtotal"] for i in cart["items"])
    assert cart["total"] == expected_total


def test_checkout_empty_cart_card_rejected(base_url):
    _clear_cart(base_url, 66)
    resp = requests.post(
        f"{base_url}/checkout",
        headers=user_headers(66),
        json={"payment_method": "CARD"},
        timeout=15,
    )
    assert resp.status_code == 400, resp.text


def test_checkout_empty_cart_cod_rejected(base_url):
    _clear_cart(base_url, 66)
    resp = requests.post(
        f"{base_url}/checkout",
        headers=user_headers(66),
        json={"payment_method": "COD"},
        timeout=15,
    )
    assert resp.status_code == 400, resp.text


def test_checkout_empty_cart_wallet_rejected(base_url):
    _clear_cart(base_url, 66)
    resp = requests.post(
        f"{base_url}/checkout",
        headers=user_headers(66),
        json={"payment_method": "WALLET"},
        timeout=15,
    )
    assert resp.status_code == 400, resp.text


def test_wallet_pay_should_deduct_exact_amount(base_url):
    before = assert_json_response(
        requests.get(f"{base_url}/wallet", headers=user_headers(9), timeout=15),
        200,
    )["wallet_balance"]

    amount = 10
    pay = requests.post(
        f"{base_url}/wallet/pay",
        headers=user_headers(9),
        json={"amount": amount},
        timeout=15,
    )
    assert_json_response(pay, 200)

    after = assert_json_response(
        requests.get(f"{base_url}/wallet", headers=user_headers(9), timeout=15),
        200,
    )["wallet_balance"]

    deducted = round(before - after, 2)
    assert deducted == amount


def test_reviews_average_should_keep_decimal_precision(base_url):
    body = assert_json_response(
        requests.get(
            f"{base_url}/products/1/reviews",
            headers=user_headers(12),
            timeout=15,
        ),
        200,
    )
    ratings = [r["rating"] for r in body["reviews"]]
    expected_avg = sum(ratings) / len(ratings)
    assert body["average_rating"] == expected_avg


def test_support_invalid_status_value_rejected(base_url):
    create = assert_json_response(
        requests.post(
            f"{base_url}/support/ticket",
            headers=user_headers(13),
            json={"subject": "Invalid status check", "message": "message body"},
            timeout=15,
        ),
        200,
    )
    ticket_id = create["ticket_id"]

    resp = requests.put(
        f"{base_url}/support/tickets/{ticket_id}",
        headers=user_headers(13),
        json={"status": "REOPENED"},
        timeout=15,
    )
    assert resp.status_code == 400, resp.text


def test_support_open_to_closed_direct_transition_rejected(base_url):
    create = assert_json_response(
        requests.post(
            f"{base_url}/support/ticket",
            headers=user_headers(13),
            json={"subject": "Open to closed", "message": "message body"},
            timeout=15,
        ),
        200,
    )
    ticket_id = create["ticket_id"]

    resp = requests.put(
        f"{base_url}/support/tickets/{ticket_id}",
        headers=user_headers(13),
        json={"status": "CLOSED"},
        timeout=15,
    )
    assert resp.status_code == 400, resp.text


def test_support_closed_to_in_progress_transition_rejected(base_url):
    create = assert_json_response(
        requests.post(
            f"{base_url}/support/ticket",
            headers=user_headers(13),
            json={"subject": "Closed to inprogress", "message": "message body"},
            timeout=15,
        ),
        200,
    )
    ticket_id = create["ticket_id"]

    assert_json_response(
        requests.put(
            f"{base_url}/support/tickets/{ticket_id}",
            headers=user_headers(13),
            json={"status": "IN_PROGRESS"},
            timeout=15,
        ),
        200,
    )
    assert_json_response(
        requests.put(
            f"{base_url}/support/tickets/{ticket_id}",
            headers=user_headers(13),
            json={"status": "CLOSED"},
            timeout=15,
        ),
        200,
    )

    resp = requests.put(
        f"{base_url}/support/tickets/{ticket_id}",
        headers=user_headers(13),
        json={"status": "IN_PROGRESS"},
        timeout=15,
    )
    assert resp.status_code == 400, resp.text


def test_support_in_progress_to_open_transition_rejected(base_url):
    create = assert_json_response(
        requests.post(
            f"{base_url}/support/ticket",
            headers=user_headers(13),
            json={"subject": "Inprogress to open", "message": "message body"},
            timeout=15,
        ),
        200,
    )
    ticket_id = create["ticket_id"]

    assert_json_response(
        requests.put(
            f"{base_url}/support/tickets/{ticket_id}",
            headers=user_headers(13),
            json={"status": "IN_PROGRESS"},
            timeout=15,
        ),
        200,
    )

    resp = requests.put(
        f"{base_url}/support/tickets/{ticket_id}",
        headers=user_headers(13),
        json={"status": "OPEN"},
        timeout=15,
    )
    assert resp.status_code == 400, resp.text
