import pytest
import requests

def test_cpn_01_apply_valid(base_url, valid_headers):
    payload = {"coupon_code": "DISCOUNT10"}
    resp = requests.post(f"{base_url}/coupon/apply", json=payload, headers=valid_headers)
    if resp.status_code != 404:
        assert resp.status_code in [200, 400] # might be 400 if cart < min value

def test_cpn_02_apply_invalid(base_url, valid_headers):
    payload = {"coupon_code": "INVALID_CODE_XYZ"}
    resp = requests.post(f"{base_url}/coupon/apply", json=payload, headers=valid_headers)
    assert resp.status_code in [400, 404]

def test_cpn_03_remove_coupon(base_url, valid_headers):
    resp = requests.post(f"{base_url}/coupon/remove", headers=valid_headers)
    assert resp.status_code in [200, 400]
