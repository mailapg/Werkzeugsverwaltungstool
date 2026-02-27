"""Tests for /api/v1/departments endpoints."""
from src.test.conftest import seed_lookup_data


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
    assert r.status_code == 200
    assert client.get(f"/api/v1/getdepartment/{created['id']}").status_code == 404


def test_delete_department_with_members_reassigns(client):
    """Beim Löschen einer Abteilung werden Mitglieder einer anderen Abteilung zugewiesen."""
    ids = seed_lookup_data(client)
    fallback_dept = client.post("/api/v1/createdepartment", json={"name": "Fallback"}).json()
    dept_to_delete = client.post("/api/v1/createdepartment", json={"name": "Löschabt"}).json()
    user = client.post("/api/v1/createuser", json={
        "firstname": "Hans", "lastname": "W",
        "email": "hans@werkstatt.local", "password": "pw",
        "role_id": ids["role_id"], "department_id": dept_to_delete["id"],
    }).json()
    r = client.delete(f"/api/v1/deletedepartment/{dept_to_delete['id']}")
    assert r.status_code == 200
    updated_user = client.get(f"/api/v1/getuser/{user['id']}").json()
    assert updated_user["department_id"] != dept_to_delete["id"]


def test_delete_department_demotes_lead(client):
    """Abteilungsleiter wird auf EMPLOYEE zurückgesetzt wenn seine Abteilung gelöscht wird."""
    ids = seed_lookup_data(client)
    client.post("/api/v1/createrole", json={"name": "DEPARTMENT_MANAGER"})
    fallback = client.post("/api/v1/createdepartment", json={"name": "Fallback"}).json()
    dept = client.post("/api/v1/createdepartment", json={"name": "Zu löschen"}).json()
    user = client.post("/api/v1/createuser", json={
        "firstname": "Chef", "lastname": "X",
        "email": "chefx@werkstatt.local", "password": "pw",
        "role_id": ids["role_id"], "department_id": dept["id"],
    }).json()
    client.patch(f"/api/v1/updatedepartment/{dept['id']}", json={"lead_user_id": user["id"]})
    client.delete(f"/api/v1/deletedepartment/{dept['id']}")
    demoted = client.get(f"/api/v1/getuser/{user['id']}").json()
    assert demoted["role"]["name"] == "EMPLOYEE"
    assert demoted["department_id"] != dept["id"]


def test_delete_last_department_with_members_rejected(client):
    """Letzter Abteilung kann nicht gelöscht werden wenn noch Mitglieder vorhanden sind."""
    ids = seed_lookup_data(client)
    # ids["department_id"] ist die einzige Abteilung; sie hat bereits einen User (durch seed_lookup_data implizit)
    user = client.post("/api/v1/createuser", json={
        "firstname": "Solo", "lastname": "Y",
        "email": "solo@werkstatt.local", "password": "pw",
        "role_id": ids["role_id"], "department_id": ids["department_id"],
    }).json()
    r = client.delete(f"/api/v1/deletedepartment/{ids['department_id']}")
    assert r.status_code == 409


def test_duplicate_lead_user_rejected(client):
    """Regression: derselbe User darf nicht Leiter zweier Abteilungen sein."""
    ids = seed_lookup_data(client)
    user = client.post("/api/v1/createuser", json={
        "firstname": "Chef", "lastname": "Müller",
        "email": "chef@werkstatt.local", "password": "pw",
        "role_id": ids["role_id"], "department_id": ids["department_id"],
    }).json()
    dept_a = client.post("/api/v1/createdepartment", json={"name": "Abt A"}).json()
    dept_b = client.post("/api/v1/createdepartment", json={"name": "Abt B"}).json()
    client.patch(f"/api/v1/updatedepartment/{dept_a['id']}", json={"lead_user_id": user["id"]})
    r = client.patch(f"/api/v1/updatedepartment/{dept_b['id']}", json={"lead_user_id": user["id"]})
    assert r.status_code == 409


def test_set_lead_promotes_to_manager(client):
    """User wird automatisch DEPARTMENT_MANAGER wenn er Abteilungsleiter wird."""
    ids = seed_lookup_data(client)
    # Role DEPARTMENT_MANAGER anlegen
    mgr_role = client.post("/api/v1/createrole", json={"name": "DEPARTMENT_MANAGER"}).json()
    user = client.post("/api/v1/createuser", json={
        "firstname": "Max", "lastname": "Muster",
        "email": "max@werkstatt.local", "password": "pw",
        "role_id": ids["role_id"], "department_id": ids["department_id"],
    }).json()
    dept = client.post("/api/v1/createdepartment", json={"name": "Neue Abt"}).json()
    client.patch(f"/api/v1/updatedepartment/{dept['id']}", json={"lead_user_id": user["id"]})
    updated_user = client.get(f"/api/v1/getuser/{user['id']}").json()
    assert updated_user["role"]["name"] == "DEPARTMENT_MANAGER"
    assert updated_user["department_id"] == dept["id"]


def test_replace_lead_demotes_old_manager(client):
    """Alter Abteilungsleiter wird auf EMPLOYEE zurückgesetzt wenn er ersetzt wird."""
    ids = seed_lookup_data(client)
    emp_role_id = ids["role_id"]
    client.post("/api/v1/createrole", json={"name": "DEPARTMENT_MANAGER"})
    user_a = client.post("/api/v1/createuser", json={
        "firstname": "Alt", "lastname": "Chef",
        "email": "alt@werkstatt.local", "password": "pw",
        "role_id": emp_role_id, "department_id": ids["department_id"],
    }).json()
    user_b = client.post("/api/v1/createuser", json={
        "firstname": "Neu", "lastname": "Chef",
        "email": "neu@werkstatt.local", "password": "pw",
        "role_id": emp_role_id, "department_id": ids["department_id"],
    }).json()
    dept = client.post("/api/v1/createdepartment", json={"name": "Abt X"}).json()
    client.patch(f"/api/v1/updatedepartment/{dept['id']}", json={"lead_user_id": user_a["id"]})
    client.patch(f"/api/v1/updatedepartment/{dept['id']}", json={"lead_user_id": user_b["id"]})
    old_lead = client.get(f"/api/v1/getuser/{user_a['id']}").json()
    assert old_lead["role"]["name"] == "EMPLOYEE"


def test_remove_lead_demotes_to_employee(client):
    """Abteilungsleiter wird auf EMPLOYEE zurückgesetzt wenn lead_user_id auf null gesetzt wird."""
    ids = seed_lookup_data(client)
    client.post("/api/v1/createrole", json={"name": "DEPARTMENT_MANAGER"})
    user = client.post("/api/v1/createuser", json={
        "firstname": "Ex", "lastname": "Chef",
        "email": "ex@werkstatt.local", "password": "pw",
        "role_id": ids["role_id"], "department_id": ids["department_id"],
    }).json()
    dept = client.post("/api/v1/createdepartment", json={"name": "Abt Y"}).json()
    client.patch(f"/api/v1/updatedepartment/{dept['id']}", json={"lead_user_id": user["id"]})
    client.patch(f"/api/v1/updatedepartment/{dept['id']}", json={"lead_user_id": None})
    demoted = client.get(f"/api/v1/getuser/{user['id']}").json()
    assert demoted["role"]["name"] == "EMPLOYEE"


def test_remove_lead_auto_promotes_successor(client):
    """Wenn lead_user_id auf null gesetzt wird und Mitarbeiter vorhanden sind, wird ein zufälliger befördert."""
    ids = seed_lookup_data(client)
    client.post("/api/v1/createrole", json={"name": "DEPARTMENT_MANAGER"})
    dept = client.post("/api/v1/createdepartment", json={"name": "Abt Z"}).json()
    lead = client.post("/api/v1/createuser", json={
        "firstname": "Alt", "lastname": "Chef",
        "email": "altchef@test.local", "password": "pw",
        "role_id": ids["role_id"], "department_id": dept["id"],
    }).json()
    emp = client.post("/api/v1/createuser", json={
        "firstname": "Nach", "lastname": "Folger",
        "email": "nachfolger@test.local", "password": "pw",
        "role_id": ids["role_id"], "department_id": dept["id"],
    }).json()
    client.patch(f"/api/v1/updatedepartment/{dept['id']}", json={"lead_user_id": lead["id"]})
    # Lead auf null setzen → Nachfolger soll befördert werden
    client.patch(f"/api/v1/updatedepartment/{dept['id']}", json={"lead_user_id": None})
    updated_emp = client.get(f"/api/v1/getuser/{emp['id']}").json()
    assert updated_emp["role"]["name"] == "DEPARTMENT_MANAGER"
    updated_dept = client.get(f"/api/v1/getdepartment/{dept['id']}").json()
    assert updated_dept["lead_user_id"] == emp["id"]
