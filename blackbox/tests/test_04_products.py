import pytest
import requests

def test_prd_01_get_products(base_url, valid_headers):
    resp = requests.get(f"{base_url}/products", headers=valid_headers)
    assert resp.status_code == 200
    if len(resp.json()) > 0:
        assert "product_id" in resp.json()[0]

def test_prd_02_filter_category(base_url, valid_headers):
    resp = requests.get(f"{base_url}/products?category=Electronics", headers=valid_headers)
    assert resp.status_code == 200

def test_prd_03_search_name(base_url, valid_headers):
    resp = requests.get(f"{base_url}/products?name=Phone", headers=valid_headers)
    assert resp.status_code == 200

def test_prd_04_get_product_id(base_url, valid_headers):
    resp = requests.get(f"{base_url}/products/1", headers=valid_headers)
    if resp.status_code != 404:
        assert resp.status_code == 200
