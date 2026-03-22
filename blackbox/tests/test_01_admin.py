import pytest
import requests

def test_adm_01_get_users(base_url, admin_headers):
    resp = requests.get(f"{base_url}/admin/users", headers=admin_headers)
    assert resp.status_code == 200
    if resp.json():
        assert "wallet_balance" in resp.json()[0]

def test_adm_02_get_user_by_id(base_url, admin_headers):
    resp = requests.get(f"{base_url}/admin/users/1", headers=admin_headers)
    if resp.status_code == 200:
        assert str(resp.json().get("user_id")) == "1"

def test_adm_03_invalid_user_id(base_url, admin_headers):
    resp = requests.get(f"{base_url}/admin/users/abc", headers=admin_headers)
    assert resp.status_code in [400, 404]

def test_adm_04_get_carts(base_url, admin_headers):
    resp = requests.get(f"{base_url}/admin/carts", headers=admin_headers)
    assert resp.status_code == 200

def test_adm_05_get_orders(base_url, admin_headers):
    resp = requests.get(f"{base_url}/admin/orders", headers=admin_headers)
    assert resp.status_code == 200

def test_adm_06_get_products(base_url, admin_headers):
    resp = requests.get(f"{base_url}/admin/products", headers=admin_headers)
    assert resp.status_code == 200

def test_adm_07_get_coupons(base_url, admin_headers):
    resp = requests.get(f"{base_url}/admin/coupons", headers=admin_headers)
    assert resp.status_code == 200

def test_adm_08_get_tickets(base_url, admin_headers):
    resp = requests.get(f"{base_url}/admin/tickets", headers=admin_headers)
    assert resp.status_code == 200

def test_adm_09_get_addresses(base_url, admin_headers):
    resp = requests.get(f"{base_url}/admin/addresses", headers=admin_headers)
    assert resp.status_code == 200
