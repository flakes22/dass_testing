import pytest
import requests

def test_hdr_01_valid_headers(base_url, valid_headers):
    resp = requests.get(f"{base_url}/profile", headers=valid_headers)
    assert resp.status_code == 200

def test_hdr_02_missing_headers(base_url):
    resp = requests.get(f"{base_url}/profile")
    assert resp.status_code in [400, 401]

def test_hdr_03_invalid_format(base_url):
    headers = {"X-Roll-Number": "abc", "X-User-ID": "-5"}
    resp = requests.get(f"{base_url}/profile", headers=headers)
    assert resp.status_code == 400

def test_hdr_04_nonexistent_user(base_url):
    headers = {"X-Roll-Number": "12345", "X-User-ID": "999999"}
    resp = requests.get(f"{base_url}/profile", headers=headers)
    assert resp.status_code in [400, 404]
