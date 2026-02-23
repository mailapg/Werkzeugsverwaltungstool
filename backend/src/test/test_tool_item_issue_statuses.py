"""Tests for /api/v1/tool-item-issue-statuses endpoints."""

def test_create_issue_status(client):
    r = client.post("/api/v1/createtoolitemissuestatus", json={"name": "OPEN"})
    assert r.status_code == 201
    assert r.json()["name"] == "OPEN"

def test_get_issue_statuses(client):
    client.post("/api/v1/createtoolitemissuestatus", json={"name": "IN_PROGRESS"})
    r = client.get("/api/v1/gettoolitemissuestatuses")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_get_issue_status_by_id(client):
    created = client.post("/api/v1/createtoolitemissuestatus", json={"name": "RESOLVED"}).json()
    r = client.get(f"/api/v1/gettoolitemissuestatus/{created['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "RESOLVED"

def test_get_issue_status_not_found(client):
    assert client.get("/api/v1/gettoolitemissuestatus/9999").status_code == 404

def test_update_issue_status(client):
    created = client.post("/api/v1/createtoolitemissuestatus", json={"name": "OPEN"}).json()
    r = client.patch(f"/api/v1/updatetoolitemissuestatus/{created['id']}", json={"name": "CLOSED"})
    assert r.status_code == 200
    assert r.json()["name"] == "CLOSED"

def test_delete_issue_status(client):
    created = client.post("/api/v1/createtoolitemissuestatus", json={"name": "TEMP"}).json()
    assert client.delete(f"/api/v1/deletetoolitemissuestatus/{created['id']}").status_code == 204
    assert client.get(f"/api/v1/gettoolitemissuestatus/{created['id']}").status_code == 404
