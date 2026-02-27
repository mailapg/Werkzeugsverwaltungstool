"""Tests for /api/v1/tool-statuses endpoints."""

def test_create_tool_status(client):
    r = client.post("/api/v1/createtoolstatus", json={"name": "AVAILABLE"})
    assert r.status_code == 201
    assert r.json()["name"] == "AVAILABLE"

def test_get_tool_statuses(client):
    client.post("/api/v1/createtoolstatus", json={"name": "LOANED"})
    r = client.get("/api/v1/gettoolstatuses")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_get_tool_status_by_id(client):
    created = client.post("/api/v1/createtoolstatus", json={"name": "DEFECT"}).json()
    r = client.get(f"/api/v1/gettoolstatus/{created['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "DEFECT"

def test_get_tool_status_not_found(client):
    assert client.get("/api/v1/gettoolstatus/9999").status_code == 404

def test_update_tool_status(client):
    created = client.post("/api/v1/createtoolstatus", json={"name": "OLD"}).json()
    r = client.patch(f"/api/v1/updatetoolstatus/{created['id']}", json={"name": "MAINTENANCE"})
    assert r.status_code == 200
    assert r.json()["name"] == "MAINTENANCE"

def test_delete_tool_status(client):
    created = client.post("/api/v1/createtoolstatus", json={"name": "TEMP"}).json()
    assert client.delete(f"/api/v1/deletetoolstatus/{created['id']}").status_code == 200
    assert client.get(f"/api/v1/gettoolstatus/{created['id']}").status_code == 404
