import pytest
import requests

def test_prf_01_get_profile(base_url, valid_headers):
    resp = requests.get(f"{base_url}/profile", headers=valid_headers)
    assert resp.status_code == 200
    assert "name" in resp.json()

def test_prf_02_put_profile_valid(base_url, valid_headers):
    payload = {"name": "Test User", "phone": "1234567890"}
    resp = requests.put(f"{base_url}/profile", json=payload, headers=valid_headers)
    assert resp.status_code == 200

def test_prf_03_put_profile_invalid_name(base_url, valid_headers):
    payload = {"name": "A", "phone": "1234567890"}
    resp = requests.put(f"{base_url}/profile", json=payload, headers=valid_headers)
    assert resp.status_code == 400

def test_prf_04_put_profile_invalid_phone(base_url, valid_headers):
    payload = {"name": "Test", "phone": "1234567"}
    resp = requests.put(f"{base_url}/profile", json=payload, headers=valid_headers)
    assert resp.status_code == 400

def test_prf_05_put_profile_missing_fields(base_url, valid_headers):
    resp = requests.put(f"{base_url}/profile", json={}, headers=valid_headers)
    assert resp.status_code == 400
