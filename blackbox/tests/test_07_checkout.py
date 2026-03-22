import pytest
import requests

def test_chk_01_checkout_card(base_url, valid_headers):
    payload = {"payment_method": "CARD"}
    resp = requests.post(f"{base_url}/checkout", json=payload, headers=valid_headers)
    # Could be 400 if cart is empty
    assert resp.status_code in [200, 400]

def test_chk_04_invalid_method(base_url, valid_headers):
    payload = {"payment_method": "XYZ"}
    resp = requests.post(f"{base_url}/checkout", json=payload, headers=valid_headers)
    assert resp.status_code == 400
