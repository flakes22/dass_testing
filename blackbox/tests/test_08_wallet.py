from conftest import assert_json_response, user_headers


USER_ID = 9


def test_wallet_get_structure(base_url):
    import requests

    resp = requests.get(
        f"{base_url}/wallet",
        headers=user_headers(USER_ID),
        timeout=15,
    )
    body = assert_json_response(resp, 200)
    assert "wallet_balance" in body


def test_wallet_add_rejects_zero_and_above_max(base_url):
    import requests

    r1 = requests.post(
        f"{base_url}/wallet/add",
        headers=user_headers(USER_ID),
        json={"amount": 0},
        timeout=15,
    )
    assert_json_response(r1, 400)

    r2 = requests.post(
        f"{base_url}/wallet/add",
        headers=user_headers(USER_ID),
        json={"amount": 100001},
        timeout=15,
    )
    assert_json_response(r2, 400)


def test_wallet_pay_insufficient_balance_rejected(base_url):
    import requests

    resp = requests.post(
        f"{base_url}/wallet/pay",
        headers=user_headers(USER_ID),
        json={"amount": 10_000_000},
        timeout=15,
    )
    assert_json_response(resp, 400)
