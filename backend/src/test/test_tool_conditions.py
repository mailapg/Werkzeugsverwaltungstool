"""Tests for /api/v1/tool-conditions endpoints."""

def test_create_tool_condition(client):
    r = client.post("/api/v1/createtoolcondition", json={"name": "OK"})
    assert r.status_code == 201
    assert r.json()["name"] == "OK"

def test_get_tool_conditions(client):
    client.post("/api/v1/createtoolcondition", json={"name": "WORN"})
    r = client.get("/api/v1/gettoolconditions")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_get_tool_condition_by_id(client):
    created = client.post("/api/v1/createtoolcondition", json={"name": "DEFECT"}).json()
    r = client.get(f"/api/v1/gettoolcondition/{created['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "DEFECT"

def test_get_tool_condition_not_found(client):
    assert client.get("/api/v1/gettoolcondition/9999").status_code == 404

def test_update_tool_condition(client):
    created = client.post("/api/v1/createtoolcondition", json={"name": "OLD"}).json()
    r = client.patch(f"/api/v1/updatetoolcondition/{created['id']}", json={"name": "WORN"})
    assert r.status_code == 200
    assert r.json()["name"] == "WORN"

def test_delete_tool_condition(client):
    created = client.post("/api/v1/createtoolcondition", json={"name": "TEMP"}).json()
    assert client.delete(f"/api/v1/deletetoolcondition/{created['id']}").status_code == 200
    assert client.get(f"/api/v1/gettoolcondition/{created['id']}").status_code == 404
