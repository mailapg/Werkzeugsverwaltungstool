"""Tests for /api/v1/users endpoints."""
from src.test.conftest import seed_lookup_data


def test_create_user(client):
    ids = seed_lookup_data(client)
    r = client.post(
        "/api/v1/createuser",
        json={
            "firstname": "Anna",
            "lastname": "Schmidt",
            "email": "anna@example.com",
            "password": "Secret123!",
            "role_id": ids["role_id"],
            "department_id": ids["department_id"],
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "anna@example.com"
    assert "password" not in data
    assert "passwordhash" not in data


def test_get_users_list(client):
    ids = seed_lookup_data(client)
    client.post("/api/v1/createuser", json={"firstname": "Bob","lastname": "B","email": "bob@example.com","password": "pw","role_id": ids["role_id"],"department_id": ids["department_id"]})
    r = client.get("/api/v1/getusers")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_user_by_id(client):
    ids = seed_lookup_data(client)
    created = client.post("/api/v1/createuser", json={"firstname": "Clara","lastname": "S","email": "clara@example.com","password": "pw","role_id": ids["role_id"],"department_id": ids["department_id"]}).json()
    r = client.get(f"/api/v1/getuser/{created['id']}")
    assert r.status_code == 200
    assert r.json()["email"] == "clara@example.com"


def test_get_user_not_found(client):
    assert client.get("/api/v1/getuser/9999").status_code == 404


def test_duplicate_email_rejected(client):
    ids = seed_lookup_data(client)
    payload = {"firstname": "Dupe","lastname": "T","email": "dupe@example.com","password": "pw","role_id": ids["role_id"],"department_id": ids["department_id"]}
    client.post("/api/v1/createuser", json=payload)
    r = client.post("/api/v1/createuser", json=payload)
    assert r.status_code == 409


def test_update_user(client):
    ids = seed_lookup_data(client)
    created = client.post("/api/v1/createuser", json={"firstname": "Old","lastname": "N","email": "update@example.com","password": "pw","role_id": ids["role_id"],"department_id": ids["department_id"]}).json()
    r = client.patch(f"/api/v1/updateuser/{created['id']}", json={"firstname": "New"})
    assert r.status_code == 200
    assert r.json()["firstname"] == "New"


def test_delete_user(client):
    ids = seed_lookup_data(client)
    created = client.post("/api/v1/createuser", json={"firstname": "Del","lastname": "M","email": "del@example.com","password": "pw","role_id": ids["role_id"],"department_id": ids["department_id"]}).json()
    assert client.delete(f"/api/v1/deleteuser/{created['id']}").status_code == 204
    assert client.get(f"/api/v1/getuser/{created['id']}").status_code == 404
