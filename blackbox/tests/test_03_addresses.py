from conftest import assert_json_response, user_headers


USER_ID = 5


def test_address_create_invalid_label_rejected(base_url):
    payload = {
        "label": "home",
        "street": "12345 Main Street",
        "city": "Hyderabad",
        "pincode": "500001",
        "is_default": False,
    }
    import requests

    resp = requests.post(
        f"{base_url}/addresses",
        headers=user_headers(USER_ID),
        json=payload,
        timeout=15,
    )
    assert_json_response(resp, 400)


def test_address_create_invalid_pincode_wrong_length_rejected(base_url):
    payload = {
        "label": "HOME",
        "street": "12345 Main Street",
        "city": "Hyderabad",
        "pincode": "50001",
        "is_default": False,
    }
    import requests

    resp = requests.post(
        f"{base_url}/addresses",
        headers=user_headers(USER_ID),
        json=payload,
        timeout=15,
    )
    assert_json_response(resp, 400)


def test_address_update_response_must_return_updated_data(base_url):
    import requests

    create_payload = {
        "label": "HOME",
        "street": "98765 Testing Avenue",
        "city": "Pune",
        "pincode": "411001",
        "is_default": False,
    }
    create = requests.post(
        f"{base_url}/addresses",
        headers=user_headers(USER_ID),
        json=create_payload,
        timeout=15,
    )
    created = assert_json_response(create, 200)
    address_id = created["address"]["address_id"]

    new_street = "11111 New Street"
    update = requests.put(
        f"{base_url}/addresses/{address_id}",
        headers=user_headers(USER_ID),
        json={"street": new_street, "is_default": True},
        timeout=15,
    )
    updated = assert_json_response(update, 200)

    assert updated["address"]["street"] == new_street
