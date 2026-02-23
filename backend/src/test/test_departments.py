"""Tests for /api/v1/departments endpoints."""


def test_create_department(client):
    r = client.post("/api/v1/createdepartment", json={"name": "Workshop"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Workshop"
    assert data["lead_user_id"] is None


def test_get_departments_list(client):
    client.post("/api/v1/createdepartment", json={"name": "Storage"})
    r = client.get("/api/v1/getdepartments")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_department_by_id(client):
    created = client.post("/api/v1/createdepartment", json={"name": "Office"}).json()
    r = client.get(f"/api/v1/getdepartment/{created['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "Office"


def test_get_department_not_found(client):
    r = client.get("/api/v1/getdepartment/9999")
    assert r.status_code == 404


def test_update_department(client):
    created = client.post("/api/v1/createdepartment", json={"name": "Old"}).json()
    r = client.patch(f"/api/v1/updatedepartment/{created['id']}", json={"name": "New"})
    assert r.status_code == 200
    assert r.json()["name"] == "New"


def test_delete_department(client):
    created = client.post("/api/v1/createdepartment", json={"name": "Temp"}).json()
    r = client.delete(f"/api/v1/deletedepartment/{created['id']}")
    assert r.status_code == 204
    assert client.get(f"/api/v1/getdepartment/{created['id']}").status_code == 404
