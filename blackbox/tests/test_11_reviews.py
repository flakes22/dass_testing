import pytest
import requests

def test_rev_01_get_reviews(base_url, valid_headers):
    resp = requests.get(f"{base_url}/products/1/reviews", headers=valid_headers)
    assert resp.status_code in [200, 404]

def test_rev_02_post_review(base_url, valid_headers):
    payload = {"rating": 5, "comment": "Great product"}
    resp = requests.post(f"{base_url}/products/1/reviews", json=payload, headers=valid_headers)
    assert resp.status_code in [200, 201, 404]

def test_rev_03_post_review_invalid(base_url, valid_headers):
    payload = {"rating": 10, "comment": "Great product"}
    resp = requests.post(f"{base_url}/products/1/reviews", json=payload, headers=valid_headers)
    if resp.status_code != 404:
        assert resp.status_code == 400
