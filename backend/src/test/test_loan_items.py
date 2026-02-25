"""Tests for loan item endpoints."""
from src.test.conftest import seed_lookup_data, create_tool, create_tool_item, create_user


def _setup_loan(client, db):
    ids = seed_lookup_data(client)
    tool = create_tool(client, ids["category_id"])
    item = create_tool_item(client, tool["id"], ids["status_id"], ids["condition_id"])
    borrower = create_user(client, ids["role_id"], ids["department_id"])
    issuer = create_user(client, ids["role_id"], ids["department_id"], email="issuer@example.com")
    return {"ids": ids, "tool": tool, "tool_item_id": item["id"], "borrower_id": borrower["id"], "issuer_id": issuer["id"]}


def _create_loan(client, setup):
    r = client.post("/api/v1/createloan", json={
        "borrower_user_id": setup["borrower_id"],
        "issued_by_user_id": setup["issuer_id"],
        "due_at": "2026-03-15T12:00:00Z",
        "items": [{"tool_item_id": setup["tool_item_id"]}],
    })
    assert r.status_code == 201
    return r.json()


def test_get_loan_items(client, db):
    setup = _setup_loan(client, db)
    _create_loan(client, setup)
    r = client.get("/api/v1/getloanitems")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_loan_item_by_id(client, db):
    setup = _setup_loan(client, db)
    loan = _create_loan(client, setup)
    item_id = loan["items"][0]["id"]
    r = client.get(f"/api/v1/getloanitem/{item_id}")
    assert r.status_code == 200
    assert r.json()["id"] == item_id


def test_get_loan_item_not_found(client, db):
    assert client.get("/api/v1/getloanitem/9999").status_code == 404


def test_create_loan_item(client, db):
    setup = _setup_loan(client, db)
    loan = _create_loan(client, setup)
    item2 = create_tool_item(
        client, setup["tool"]["id"], setup["ids"]["status_id"], setup["ids"]["condition_id"],
        inventory_no="INV-002",
    )
    r = client.post("/api/v1/createloanitem", json={"loan_id": loan["id"], "tool_item_id": item2["id"]})
    assert r.status_code == 201
    assert r.json()["tool_item"]["id"] == item2["id"]


def test_update_loan_item(client, db):
    setup = _setup_loan(client, db)
    loan = _create_loan(client, setup)
    item_id = loan["items"][0]["id"]
    r = client.patch(f"/api/v1/updateloanitem/{item_id}", json={"return_comment": "All good"})
    assert r.status_code == 200
    assert r.json()["return_comment"] == "All good"


def test_delete_loan_item(client, db):
    setup = _setup_loan(client, db)
    loan = _create_loan(client, setup)
    item_id = loan["items"][0]["id"]
    assert client.delete(f"/api/v1/deleteloanitem/{item_id}").status_code == 204
    assert client.get(f"/api/v1/getloanitem/{item_id}").status_code == 404
