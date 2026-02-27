"""Tests for /api/v1/roles endpoints."""


def test_create_role(client):
    r = client.post("/api/v1/createrole", json={"name": "ADMIN"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "ADMIN"
    assert "id" in data


def test_get_roles_list(client):
    client.post("/api/v1/createrole", json={"name": "EMPLOYEE"})
    r = client.get("/api/v1/getroles")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_role_by_id(client):
    created = client.post("/api/v1/createrole", json={"name": "ADMIN"}).json()
    r = client.get(f"/api/v1/getrole/{created['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "ADMIN"


def test_get_role_not_found(client):
    r = client.get("/api/v1/getrole/9999")
    assert r.status_code == 404


def test_update_role(client):
    created = client.post("/api/v1/createrole", json={"name": "EMPLOYEE"}).json()
    r = client.patch(f"/api/v1/updaterole/{created['id']}", json={"name": "AZUBI"})
    assert r.status_code == 200
    assert r.json()["name"] == "AZUBI"


def test_update_role_not_found(client):
    r = client.patch("/api/v1/updaterole/9999", json={"name": "X"})
    assert r.status_code == 404


def test_delete_role(client):
    created = client.post("/api/v1/createrole", json={"name": "TEMP"}).json()
    r = client.delete(f"/api/v1/deleterole/{created['id']}")
    assert r.status_code == 200
    assert client.get(f"/api/v1/getrole/{created['id']}").status_code == 404


def test_delete_role_not_found(client):
    r = client.delete("/api/v1/deleterole/9999")
    assert r.status_code == 404
