import pytest
import requests

def test_tkt_01_create_ticket(base_url, valid_headers):
    payload = {"subject": "Need help", "message": "My order is delayed."}
    resp = requests.post(f"{base_url}/support/ticket", json=payload, headers=valid_headers)
    assert resp.status_code in [200, 201]

def test_tkt_02_create_ticket_invalid(base_url, valid_headers):
    payload = {"subject": "A", "message": "My order is delayed."}
    resp = requests.post(f"{base_url}/support/ticket", json=payload, headers=valid_headers)
    assert resp.status_code == 400

def test_tkt_03_get_tickets(base_url, valid_headers):
    resp = requests.get(f"{base_url}/support/tickets", headers=valid_headers)
    assert resp.status_code == 200

def test_tkt_04_update_ticket(base_url, valid_headers):
    payload = {"status": "IN_PROGRESS"}
    resp = requests.put(f"{base_url}/support/tickets/1", json=payload, headers=valid_headers)
    assert resp.status_code in [200, 404, 400]
