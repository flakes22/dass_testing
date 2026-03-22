import pytest
import requests

def test_wlt_01_get_wallet(base_url, valid_headers):
    resp = requests.get(f"{base_url}/wallet", headers=valid_headers)
    assert resp.status_code == 200

def test_wlt_02_add_wallet_valid(base_url, valid_headers):
    payload = {"amount": 500}
    resp = requests.post(f"{base_url}/wallet/add", json=payload, headers=valid_headers)
    assert resp.status_code == 200

def test_wlt_03_add_wallet_invalid(base_url, valid_headers):
    payload = {"amount": -10}
    resp = requests.post(f"{base_url}/wallet/add", json=payload, headers=valid_headers)
    assert resp.status_code == 400

def test_wlt_04_pay_wallet_valid(base_url, valid_headers):
    payload = {"amount": 50}
    resp = requests.post(f"{base_url}/wallet/pay", json=payload, headers=valid_headers)
    # Could be 200 or 400 if insufficient
    assert resp.status_code in [200, 400]

def test_wlt_05_pay_wallet_invalid(base_url, valid_headers):
    payload = {"amount": -50}
    resp = requests.post(f"{base_url}/wallet/pay", json=payload, headers=valid_headers)
    assert resp.status_code == 400
