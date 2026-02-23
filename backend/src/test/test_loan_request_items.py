"""Tests for loan request item endpoints."""
from src.test.conftest import seed_lookup_data, create_tool, create_user


def _setup(client, db):
    from src.app.models.loan_request_status import LoanRequestStatus
    ids = seed_lookup_data(client)
    tool = create_tool(client, ids["category_id"])
    user = create_user(client, ids["role_id"], ids["department_id"])
    s = LoanRequestStatus(name="REQUESTED")
    db.add(s); db.commit()
    return {"ids": ids, "tool": tool, "tool_id": tool["id"], "user_id": user["id"], "status_id": s.id}


def _create_loan_request(client, setup):
    r = client.post("/api/v1/createloanrequest", json={
        "requester_user_id": setup["user_id"],
        "due_at": "2026-03-01T10:00:00Z",
        "items": [{"tool_id": setup["tool_id"], "quantity": 1}],
    })
    assert r.status_code == 201
    return r.json()


def test_get_loan_request_items(client, db):
    setup = _setup(client, db)
    _create_loan_request(client, setup)
    r = client.get("/api/v1/getloanrequestitems")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_loan_request_item_by_id(client, db):
    setup = _setup(client, db)
    req = _create_loan_request(client, setup)
    item_id = req["items"][0]["id"]
    r = client.get(f"/api/v1/getloanrequestitem/{item_id}")
    assert r.status_code == 200
    assert r.json()["id"] == item_id


def test_get_loan_request_item_not_found(client, db):
    assert client.get("/api/v1/getloanrequestitem/9999").status_code == 404


def test_create_loan_request_item(client, db):
    setup = _setup(client, db)
    req = _create_loan_request(client, setup)
    tool2 = create_tool(client, setup["ids"]["category_id"], name="Screwdriver")
    r = client.post("/api/v1/createloanrequestitem", json={
        "request_id": req["id"],
        "tool_id": tool2["id"],
        "quantity": 3,
    })
    assert r.status_code == 201
    assert r.json()["tool"]["id"] == tool2["id"]
    assert r.json()["quantity"] == 3


def test_update_loan_request_item(client, db):
    setup = _setup(client, db)
    req = _create_loan_request(client, setup)
    item_id = req["items"][0]["id"]
    r = client.patch(f"/api/v1/updateloanrequestitem/{item_id}", json={"quantity": 5})
    assert r.status_code == 200
    assert r.json()["quantity"] == 5


def test_delete_loan_request_item(client, db):
    setup = _setup(client, db)
    req = _create_loan_request(client, setup)
    item_id = req["items"][0]["id"]
    assert client.delete(f"/api/v1/deleteloanrequestitem/{item_id}").status_code == 204
    assert client.get(f"/api/v1/getloanrequestitem/{item_id}").status_code == 404
