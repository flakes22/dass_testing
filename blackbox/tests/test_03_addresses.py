import pytest
import requests

def test_adr_01_get_addresses(base_url, valid_headers):
    resp = requests.get(f"{base_url}/addresses", headers=valid_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_adr_02_post_address_valid(base_url, valid_headers):
    payload = {
        "label": "HOME",
        "street": "123 Test St",
        "city": "Hyderabad",
        "pincode": "500032",
        "is_default": True
    }
    resp = requests.post(f"{base_url}/addresses", json=payload, headers=valid_headers)
    assert resp.status_code in [200, 201]

def test_adr_03_post_address_invalid_label(base_url, valid_headers):
    payload = {
        "label": "WORK",
        "street": "123 Test St",
        "city": "Hyderabad",
        "pincode": "500032"
    }
    resp = requests.post(f"{base_url}/addresses", json=payload, headers=valid_headers)
    assert resp.status_code == 400

def test_adr_04_post_address_invalid_boundaries(base_url, valid_headers):
    payload = {
        "label": "HOME",
        "street": "123", # < 5
        "city": "Hyderabad",
        "pincode": "500032"
    }
    resp = requests.post(f"{base_url}/addresses", json=payload, headers=valid_headers)
    assert resp.status_code == 400

def test_adr_05_post_address_invalid_pincode(base_url, valid_headers):
    payload = {
        "label": "HOME",
        "street": "123 Test St",
        "city": "Hyderabad",
        "pincode": "123" # != 6
    }
    resp = requests.post(f"{base_url}/addresses", json=payload, headers=valid_headers)
    assert resp.status_code == 400

def test_adr_06_put_address_valid(base_url, valid_headers):
    # Try updating address 1
    payload = {"street": "Updated St", "is_default": False}
    resp = requests.put(f"{base_url}/addresses/1", json=payload, headers=valid_headers)
    if resp.status_code != 404:
        assert resp.status_code == 200

def test_adr_07_put_address_immutable(base_url, valid_headers):
    payload = {"city": "New City"}
    resp = requests.put(f"{base_url}/addresses/1", json=payload, headers=valid_headers)
    if resp.status_code != 404:
        assert resp.status_code == 400

def test_adr_08_delete_address(base_url, valid_headers):
    resp = requests.delete(f"{base_url}/addresses/99999", headers=valid_headers)
    assert resp.status_code in [400, 404]
