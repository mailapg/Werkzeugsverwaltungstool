"""Tests for /api/v1/users endpoints."""
from src.test.conftest import seed_lookup_data


def test_create_user(client):
    ids = seed_lookup_data(client)
    r = client.post(
        "/api/v1/createuser",
        json={
            "firstname": "Anna",
            "lastname": "Schmidt",
            "email": "aschmidt@werkstatt.local",
            "password": "Secret123!",
            "role_id": ids["role_id"],
            "department_id": ids["department_id"],
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "aschmidt@werkstatt.local"
    assert "password" not in data
    assert "passwordhash" not in data


def test_get_users_list(client):
    ids = seed_lookup_data(client)
    client.post("/api/v1/createuser", json={"firstname": "Bob","lastname": "B","email": "bbraun@lager.local","password": "pw","role_id": ids["role_id"],"department_id": ids["department_id"]})
    r = client.get("/api/v1/getusers")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_user_by_id(client):
    ids = seed_lookup_data(client)
    created = client.post("/api/v1/createuser", json={"firstname": "Clara","lastname": "S","email": "cschmidt@elektro.local","password": "pw","role_id": ids["role_id"],"department_id": ids["department_id"]}).json()
    r = client.get(f"/api/v1/getuser/{created['id']}")
    assert r.status_code == 200
    assert r.json()["email"] == "cschmidt@elektro.local"


def test_local_domain_email_serialized_correctly(client):
    """Regression: .local-Domains dürfen bei GET nicht zu 500 führen."""
    ids = seed_lookup_data(client)
    created = client.post("/api/v1/createuser", json={"firstname": "Klaus","lastname": "Müller","email": "kmueller@werkstatt.local","password": "pw","role_id": ids["role_id"],"department_id": ids["department_id"]}).json()
    r = client.get(f"/api/v1/getuser/{created['id']}")
    assert r.status_code == 200
    assert r.json()["email"] == "kmueller@werkstatt.local"
    r_list = client.get("/api/v1/getusers")
    assert r_list.status_code == 200


def test_invalid_email_rejected(client):
    """E-Mails ohne @-Zeichen oder Domain dürfen nicht erstellt werden."""
    ids = seed_lookup_data(client)
    base = {"firstname": "X", "lastname": "Y", "password": "pw", "role_id": ids["role_id"], "department_id": ids["department_id"]}
    assert client.post("/api/v1/createuser", json={**base, "email": "keineatzeichen"}).status_code == 422
    assert client.post("/api/v1/createuser", json={**base, "email": "@keinlokal"}).status_code == 422
    assert client.post("/api/v1/createuser", json={**base, "email": "user@"}).status_code == 422


def test_get_user_not_found(client):
    assert client.get("/api/v1/getuser/9999").status_code == 404


def test_duplicate_email_rejected(client):
    ids = seed_lookup_data(client)
    payload = {"firstname": "Dupe","lastname": "T","email": "dtest@fertigung.local","password": "pw","role_id": ids["role_id"],"department_id": ids["department_id"]}
    client.post("/api/v1/createuser", json=payload)
    r = client.post("/api/v1/createuser", json=payload)
    assert r.status_code == 409


def test_update_user(client):
    ids = seed_lookup_data(client)
    created = client.post("/api/v1/createuser", json={"firstname": "Old","lastname": "N","email": "oneu@montage.local","password": "pw","role_id": ids["role_id"],"department_id": ids["department_id"]}).json()
    r = client.patch(f"/api/v1/updateuser/{created['id']}", json={"firstname": "New"})
    assert r.status_code == 200
    assert r.json()["firstname"] == "New"


def test_delete_user(client):
    ids = seed_lookup_data(client)
    created = client.post("/api/v1/createuser", json={"firstname": "Del","lastname": "M","email": "dmueller@lager.local","password": "pw","role_id": ids["role_id"],"department_id": ids["department_id"]}).json()
    assert client.delete(f"/api/v1/deleteuser/{created['id']}").status_code == 200
    assert client.get(f"/api/v1/getuser/{created['id']}").status_code == 404


def test_create_user_invalid_role_rejected(client):
    """Erstellen mit nicht-existierender role_id liefert 404."""
    ids = seed_lookup_data(client)
    r = client.post("/api/v1/createuser", json={
        "firstname": "X", "lastname": "Y", "email": "xy@test.local",
        "password": "pw", "role_id": 9999, "department_id": ids["department_id"],
    })
    assert r.status_code == 404


def test_create_user_invalid_department_rejected(client):
    """Erstellen mit nicht-existierender department_id liefert 404."""
    ids = seed_lookup_data(client)
    r = client.post("/api/v1/createuser", json={
        "firstname": "X", "lastname": "Y", "email": "xy@test.local",
        "password": "pw", "role_id": ids["role_id"], "department_id": 9999,
    })
    assert r.status_code == 404


def test_update_role_from_manager_promotes_successor(client):
    """Wenn ein Abteilungsleiter per updateuser auf EMPLOYEE gesetzt wird, bekommt ein anderer die Leiterrolle."""
    ids = seed_lookup_data(client)
    emp_role_id = ids["role_id"]
    mgr_role = client.post("/api/v1/createrole", json={"name": "DEPARTMENT_MANAGER"}).json()
    dept = client.post("/api/v1/createdepartment", json={"name": "TestAbt"}).json()

    lead = client.post("/api/v1/createuser", json={
        "firstname": "Chef", "lastname": "A",
        "email": "chefa@test.local", "password": "pw",
        "role_id": mgr_role["id"], "department_id": dept["id"],
    }).json()
    emp = client.post("/api/v1/createuser", json={
        "firstname": "Emp", "lastname": "B",
        "email": "empb@test.local", "password": "pw",
        "role_id": emp_role_id, "department_id": dept["id"],
    }).json()
    client.patch(f"/api/v1/updatedepartment/{dept['id']}", json={"lead_user_id": lead["id"]})

    # Leiter per updateuser zu EMPLOYEE machen
    client.patch(f"/api/v1/updateuser/{lead['id']}", json={"role_id": emp_role_id})

    # Employee muss jetzt DEPARTMENT_MANAGER sein
    updated_emp = client.get(f"/api/v1/getuser/{emp['id']}").json()
    assert updated_emp["role"]["name"] == "DEPARTMENT_MANAGER"

    updated_dept = client.get(f"/api/v1/getdepartment/{dept['id']}").json()
    assert updated_dept["lead_user_id"] == emp["id"]


def test_update_role_to_manager_sets_department_lead(client):
    """Wenn per updateuser Rolle auf DEPARTMENT_MANAGER gesetzt wird, wird der Nutzer Abteilungsleiter."""
    ids = seed_lookup_data(client)
    emp_role_id = ids["role_id"]
    mgr_role = client.post("/api/v1/createrole", json={"name": "DEPARTMENT_MANAGER"}).json()
    dept = client.post("/api/v1/createdepartment", json={"name": "TestAbt"}).json()

    old_lead = client.post("/api/v1/createuser", json={
        "firstname": "Alt", "lastname": "Chef",
        "email": "altc@test.local", "password": "pw",
        "role_id": emp_role_id, "department_id": dept["id"],
    }).json()
    client.patch(f"/api/v1/updatedepartment/{dept['id']}", json={"lead_user_id": old_lead["id"]})

    new_mgr = client.post("/api/v1/createuser", json={
        "firstname": "Neu", "lastname": "Mgr",
        "email": "neumgr@test.local", "password": "pw",
        "role_id": emp_role_id, "department_id": dept["id"],
    }).json()

    # Rolle auf DEPARTMENT_MANAGER hochstufen
    client.patch(f"/api/v1/updateuser/{new_mgr['id']}", json={"role_id": mgr_role["id"]})

    # Abteilung hat jetzt den neuen Nutzer als Leiter
    updated_dept = client.get(f"/api/v1/getdepartment/{dept['id']}").json()
    assert updated_dept["lead_user_id"] == new_mgr["id"]

    # Alter Leiter wurde zu EMPLOYEE
    demoted = client.get(f"/api/v1/getuser/{old_lead['id']}").json()
    assert demoted["role"]["name"] == "EMPLOYEE"


def test_update_manager_moves_to_new_dept(client):
    """DEPARTMENT_MANAGER wechselt Abteilung → alte Abt bekommt Nachfolger, neue Abt bekommt ihn als Leiter."""
    ids = seed_lookup_data(client)
    emp_role_id = ids["role_id"]
    mgr_role = client.post("/api/v1/createrole", json={"name": "DEPARTMENT_MANAGER"}).json()
    dept_a = client.post("/api/v1/createdepartment", json={"name": "Abt A"}).json()
    dept_b = client.post("/api/v1/createdepartment", json={"name": "Abt B"}).json()

    mgr = client.post("/api/v1/createuser", json={
        "firstname": "Chef", "lastname": "M",
        "email": "chefm@test.local", "password": "pw",
        "role_id": mgr_role["id"], "department_id": dept_a["id"],
    }).json()
    emp_a = client.post("/api/v1/createuser", json={
        "firstname": "Emp", "lastname": "A",
        "email": "empa@test.local", "password": "pw",
        "role_id": emp_role_id, "department_id": dept_a["id"],
    }).json()
    old_lead_b = client.post("/api/v1/createuser", json={
        "firstname": "Alt", "lastname": "B",
        "email": "altb@test.local", "password": "pw",
        "role_id": emp_role_id, "department_id": dept_b["id"],
    }).json()
    client.patch(f"/api/v1/updatedepartment/{dept_a['id']}", json={"lead_user_id": mgr["id"]})
    client.patch(f"/api/v1/updatedepartment/{dept_b['id']}", json={"lead_user_id": old_lead_b["id"]})

    # Manager in Abt B verschieben
    client.patch(f"/api/v1/updateuser/{mgr['id']}", json={"department_id": dept_b["id"]})

    # Abt A hat jetzt emp_a als Leiter
    assert client.get(f"/api/v1/getdepartment/{dept_a['id']}").json()["lead_user_id"] == emp_a["id"]
    assert client.get(f"/api/v1/getuser/{emp_a['id']}").json()["role"]["name"] == "DEPARTMENT_MANAGER"

    # Abt B hat jetzt mgr als Leiter, old_lead_b wurde demoted
    assert client.get(f"/api/v1/getdepartment/{dept_b['id']}").json()["lead_user_id"] == mgr["id"]
    assert client.get(f"/api/v1/getuser/{old_lead_b['id']}").json()["role"]["name"] == "EMPLOYEE"


def test_create_department_manager_demotes_old_lead(client):
    """Neuer Nutzer als DEPARTMENT_MANAGER → alter Leiter der Abteilung wird zu EMPLOYEE."""
    ids = seed_lookup_data(client)
    mgr_role = client.post("/api/v1/createrole", json={"name": "DEPARTMENT_MANAGER"}).json()
    dept = client.post("/api/v1/createdepartment", json={"name": "TestAbt"}).json()

    # Alten Leiter erstellen und zuweisen
    old_lead = client.post("/api/v1/createuser", json={
        "firstname": "Alt", "lastname": "Chef",
        "email": "altchef2@test.local", "password": "pw",
        "role_id": ids["role_id"], "department_id": dept["id"],
    }).json()
    client.patch(f"/api/v1/updatedepartment/{dept['id']}", json={"lead_user_id": old_lead["id"]})

    # Neuen Nutzer direkt als DEPARTMENT_MANAGER anlegen
    new_lead = client.post("/api/v1/createuser", json={
        "firstname": "Neu", "lastname": "Chef",
        "email": "neuchef2@test.local", "password": "pw",
        "role_id": mgr_role["id"], "department_id": dept["id"],
    }).json()

    # Neuer Nutzer ist jetzt Leiter
    updated_dept = client.get(f"/api/v1/getdepartment/{dept['id']}").json()
    assert updated_dept["lead_user_id"] == new_lead["id"]

    # Alter Leiter wurde zu EMPLOYEE
    demoted = client.get(f"/api/v1/getuser/{old_lead['id']}").json()
    assert demoted["role"]["name"] == "EMPLOYEE"


def test_delete_lead_promotes_random_successor(client):
    """Wenn ein Abteilungsleiter gelöscht wird, bekommt ein zufälliger Employee die Leiterrolle."""
    ids = seed_lookup_data(client)
    client.post("/api/v1/createrole", json={"name": "DEPARTMENT_MANAGER"})
    dept = client.post("/api/v1/createdepartment", json={"name": "TestAbt"}).json()

    lead = client.post("/api/v1/createuser", json={
        "firstname": "Chef", "lastname": "L", "email": "chef@test.local",
        "password": "pw", "role_id": ids["role_id"], "department_id": dept["id"],
    }).json()
    emp = client.post("/api/v1/createuser", json={
        "firstname": "Emp", "lastname": "L", "email": "emp@test.local",
        "password": "pw", "role_id": ids["role_id"], "department_id": dept["id"],
    }).json()

    # Lead setzen
    client.patch(f"/api/v1/updatedepartment/{dept['id']}", json={"lead_user_id": lead["id"]})

    # Lead löschen
    assert client.delete(f"/api/v1/deleteuser/{lead['id']}").status_code == 200

    # Employee muss jetzt DEPARTMENT_MANAGER sein
    updated_emp = client.get(f"/api/v1/getuser/{emp['id']}").json()
    assert updated_emp["role"]["name"] == "DEPARTMENT_MANAGER"

    # Abteilung muss neuen Leiter haben
    updated_dept = client.get(f"/api/v1/getdepartment/{dept['id']}").json()
    assert updated_dept["lead_user_id"] == emp["id"]
