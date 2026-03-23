from conftest import assert_json_response, user_headers


USER_ID = 11


def test_orders_list_structure(base_url):
    import requests

    resp = requests.get(
        f"{base_url}/orders",
        headers=user_headers(USER_ID),
        timeout=20,
    )
    body = assert_json_response(resp, 200)
    assert isinstance(body, list)


def test_cancel_non_existent_order_returns_404(base_url):
    import requests

    resp = requests.post(
        f"{base_url}/orders/99999999/cancel",
        headers=user_headers(USER_ID),
        timeout=15,
    )
    assert_json_response(resp, 404)
