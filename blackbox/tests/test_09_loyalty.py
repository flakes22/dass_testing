import pytest
import requests

def test_lyl_01_get_loyalty(base_url, valid_headers):
    resp = requests.get(f"{base_url}/loyalty", headers=valid_headers)
    assert resp.status_code == 200

def test_lyl_02_redeem_valid(base_url, valid_headers):
    payload = {"points": 1}
    resp = requests.post(f"{base_url}/loyalty/redeem", json=payload, headers=valid_headers)
    assert resp.status_code in [200, 400] # 400 if insufficient

def test_lyl_03_redeem_invalid(base_url, valid_headers):
    payload = {"points": -10}
    resp = requests.post(f"{base_url}/loyalty/redeem", json=payload, headers=valid_headers)
    assert resp.status_code == 400
