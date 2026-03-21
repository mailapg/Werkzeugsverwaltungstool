"""Tests for loans endpoints and return processing."""
from src.test.conftest import seed_lookup_data, create_tool, create_tool_item, create_user

def _setup_loan(client, db):
    ids = seed_lookup_data(client)
    tool = create_tool(client, ids["category_id"])
    item = create_tool_item(client, tool["id"], ids["status_id"], ids["condition_id"])
    borrower = create_user(client, ids["role_id"], ids["department_id"])
    issuer = create_user(client, ids["role_id"], ids["department_id"], email="issuer@example.com")
    return {"ids": ids, "tool_item_id": item["id"], "borrower_id": borrower["id"], "issuer_id": issuer["id"]}

def _create_loan(client, setup):
    r = client.post("/api/v1/createloan", json={"borrower_user_id": setup["borrower_id"],"issued_by_user_id": setup["issuer_id"],"due_at": "2026-03-15T12:00:00Z","items": [{"tool_item_id": setup["tool_item_id"]}]})
    assert r.status_code == 201
    return r.json()

def test_create_loan(client, db):
    setup = _setup_loan(client, db)
    loan = _create_loan(client, setup)
    assert loan["borrower"]["id"] == setup["borrower_id"]
    assert len(loan["items"]) == 1
    assert loan["returned_at"] is None

def test_tool_item_status_set_to_loaned(client, db):
    setup = _setup_loan(client, db)
    _create_loan(client, setup)
    r = client.get(f"/api/v1/gettoolitem/{setup['tool_item_id']}")
    assert r.json()["status"]["name"] == "LOANED"

def test_get_loans_list(client, db):
    setup = _setup_loan(client, db)
    _create_loan(client, setup)
    r = client.get("/api/v1/getloans")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_get_loan_by_id(client, db):
    setup = _setup_loan(client, db)
    loan = _create_loan(client, setup)
    r = client.get(f"/api/v1/getloan/{loan['id']}")
    assert r.status_code == 200

def test_get_loan_not_found(client):
    assert client.get("/api/v1/getloan/9999").status_code == 404

def test_return_loan(client, db):
    setup = _setup_loan(client, db)
    loan = _create_loan(client, setup)
    loan_item_id = loan["items"][0]["id"]
    r = client.patch(f"/api/v1/returnloan/{loan['id']}", json={"returned_by_user_id": setup["issuer_id"],"items": [{"loan_item_id": loan_item_id,"return_comment": "Everything ok","return_condition_id": setup["ids"]["condition_id"]}]})
    assert r.status_code == 200
    assert r.json()["returned_at"] is not None

def test_return_loan_twice_rejected(client, db):
    setup = _setup_loan(client, db)
    loan = _create_loan(client, setup)
    loan_item_id = loan["items"][0]["id"]
    payload = {"returned_by_user_id": setup["issuer_id"],"items": [{"loan_item_id": loan_item_id}]}
    client.patch(f"/api/v1/returnloan/{loan['id']}", json=payload)
    r = client.patch(f"/api/v1/returnloan/{loan['id']}", json=payload)
    assert r.status_code == 409

def test_delete_loan(client, db):
    setup = _setup_loan(client, db)
    loan = _create_loan(client, setup)
    assert client.delete(f"/api/v1/deleteloan/{loan['id']}").status_code == 200
    assert client.get(f"/api/v1/getloan/{loan['id']}").status_code == 404
