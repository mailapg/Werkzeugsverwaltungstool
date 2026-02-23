"""Tests for /api/v1/loan-request-statuses endpoints."""

def test_create_loan_request_status(client):
    r = client.post("/api/v1/createloanrequeststatus", json={"name": "REQUESTED"})
    assert r.status_code == 201
    assert r.json()["name"] == "REQUESTED"

def test_get_loan_request_statuses(client):
    client.post("/api/v1/createloanrequeststatus", json={"name": "APPROVED"})
    r = client.get("/api/v1/getloanrequeststatuses")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_get_loan_request_status_by_id(client):
    created = client.post("/api/v1/createloanrequeststatus", json={"name": "REJECTED"}).json()
    r = client.get(f"/api/v1/getloanrequeststatus/{created['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "REJECTED"

def test_get_loan_request_status_not_found(client):
    assert client.get("/api/v1/getloanrequeststatus/9999").status_code == 404

def test_update_loan_request_status(client):
    created = client.post("/api/v1/createloanrequeststatus", json={"name": "OLD"}).json()
    r = client.patch(f"/api/v1/updateloanrequeststatus/{created['id']}", json={"name": "CANCELLED"})
    assert r.status_code == 200
    assert r.json()["name"] == "CANCELLED"

def test_delete_loan_request_status(client):
    created = client.post("/api/v1/createloanrequeststatus", json={"name": "TEMP"}).json()
    assert client.delete(f"/api/v1/deleteloanrequeststatus/{created['id']}").status_code == 204
    assert client.get(f"/api/v1/getloanrequeststatus/{created['id']}").status_code == 404
