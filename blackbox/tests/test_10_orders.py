import pytest
import requests

def test_ord_01_get_orders(base_url, valid_headers):
    resp = requests.get(f"{base_url}/orders", headers=valid_headers)
    assert resp.status_code == 200

def test_ord_02_cancel_order(base_url, valid_headers):
    resp = requests.post(f"{base_url}/orders/1/cancel", headers=valid_headers)
    assert resp.status_code in [200, 400, 404]

def test_ord_04_invoice(base_url, valid_headers):
    resp = requests.get(f"{base_url}/orders/1/invoice", headers=valid_headers)
    assert resp.status_code in [200, 404]
