from conftest import assert_json_response, user_headers


USER_ID = 13


def test_support_ticket_subject_too_short_rejected(base_url):
    import requests

    resp = requests.post(
        f"{base_url}/support/ticket",
        headers=user_headers(USER_ID),
        json={"subject": "abcd", "message": "hello"},
        timeout=15,
    )
    assert_json_response(resp, 400)


def test_support_ticket_initial_status_open(base_url):
    import requests

    resp = requests.post(
        f"{base_url}/support/ticket",
        headers=user_headers(USER_ID),
        json={"subject": "Need help with cart", "message": "Unable to apply coupon"},
        timeout=15,
    )
    body = assert_json_response(resp, 200)
    assert body["status"] == "OPEN"


def test_support_status_transition_must_be_one_way(base_url):
    import requests

    create = requests.post(
        f"{base_url}/support/ticket",
        headers=user_headers(USER_ID),
        json={"subject": "Transition validation", "message": "Checking OPEN to CLOSED"},
        timeout=15,
    )
    created = assert_json_response(create, 200)
    ticket_id = created["ticket_id"]

    direct_close = requests.put(
        f"{base_url}/support/tickets/{ticket_id}",
        headers=user_headers(USER_ID),
        json={"status": "CLOSED"},
        timeout=15,
    )

    assert direct_close.status_code == 400, direct_close.text
