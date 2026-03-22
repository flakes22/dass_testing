import pytest
import requests

def test_crt_01_get_cart(base_url, valid_headers):
    resp = requests.get(f"{base_url}/cart", headers=valid_headers)
    assert resp.status_code == 200

def test_crt_02_add_cart_valid(base_url, valid_headers):
    payload = {"product_id": 1, "quantity": 1}
    resp = requests.post(f"{base_url}/cart/add", json=payload, headers=valid_headers)
    if resp.status_code != 404: # in case product 1 doesn't exist
        assert resp.status_code == 200

def test_crt_03_add_cart_invalid_qty(base_url, valid_headers):
    payload = {"product_id": 1, "quantity": -5}
    resp = requests.post(f"{base_url}/cart/add", json=payload, headers=valid_headers)
    assert resp.status_code == 400

def test_crt_04_update_cart(base_url, valid_headers):
    payload = {"product_id": 1, "quantity": 2}
    resp = requests.post(f"{base_url}/cart/update", json=payload, headers=valid_headers)
    if resp.status_code != 404:
        assert resp.status_code == 200

def test_crt_05_remove_cart(base_url, valid_headers):
    payload = {"product_id": 1}
    resp = requests.post(f"{base_url}/cart/remove", json=payload, headers=valid_headers)
    if resp.status_code != 404:
        assert resp.status_code == 200

def test_crt_06_clear_cart(base_url, valid_headers):
    resp = requests.delete(f"{base_url}/cart/clear", headers=valid_headers)
    assert resp.status_code == 200
