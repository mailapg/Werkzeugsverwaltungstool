"""Tests for loan requests endpoints."""
from src.test.conftest import seed_lookup_data, create_tool, create_user

def _setup(client, db):
    from src.app.models.loan_request_status import LoanRequestStatus
    ids = seed_lookup_data(client)
    tool = create_tool(client, ids["category_id"])
    user = create_user(client, ids["role_id"], ids["department_id"])
    s = LoanRequestStatus(name="REQUESTED")
    db.add(s); db.commit()
    return {"ids": ids, "tool_id": tool["id"], "user_id": user["id"], "status_id": s.id}

def test_create_loan_request(client, db):
    d = _setup(client, db)
    r = client.post("/api/v1/createloanrequest", json={"requester_user_id": d["user_id"],"due_at": "2026-03-01T10:00:00Z","comment": "For project X","items": [{"tool_id": d["tool_id"], "quantity": 2}]})
    assert r.status_code == 201
    data = r.json()
    assert data["requester"]["id"] == d["user_id"]
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2

def test_get_loan_requests_list(client, db):
    d = _setup(client, db)
    client.post("/api/v1/createloanrequest", json={"requester_user_id": d["user_id"],"due_at": "2026-03-01T10:00:00Z","items": [{"tool_id": d["tool_id"], "quantity": 1}]})
    r = client.get("/api/v1/getloanrequests")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_get_loan_request_by_id(client, db):
    d = _setup(client, db)
    req = client.post("/api/v1/createloanrequest", json={"requester_user_id": d["user_id"],"due_at": "2026-03-01T10:00:00Z","items": [{"tool_id": d["tool_id"], "quantity": 1}]}).json()
    r = client.get(f"/api/v1/getloanrequest/{req['id']}")
    assert r.status_code == 200

def test_decide_loan_request_approve(client, db):
    from src.app.models.loan_request_status import LoanRequestStatus
    d = _setup(client, db)
    approver = create_user(client, d["ids"]["role_id"], d["ids"]["department_id"], email="approver@example.com")
    approved = LoanRequestStatus(name="APPROVED")
    db.add(approved); db.commit()
    req = client.post("/api/v1/createloanrequest", json={"requester_user_id": d["user_id"],"due_at": "2026-03-01T10:00:00Z","items": [{"tool_id": d["tool_id"], "quantity": 1}]}).json()
    r = client.patch(f"/api/v1/decideloanrequest/{req['id']}", json={"approver_user_id": approver["id"],"status_id": approved.id,"decision_comment": "Approved!"})
    assert r.status_code == 200
    assert r.json()["decision_comment"] == "Approved!"
    assert r.json()["decision_at"] is not None

def test_get_loan_request_not_found(client):
    assert client.get("/api/v1/getloanrequest/9999").status_code == 404

def test_delete_loan_request(client, db):
    d = _setup(client, db)
    req = client.post("/api/v1/createloanrequest", json={"requester_user_id": d["user_id"],"due_at": "2026-03-01T10:00:00Z","items": [{"tool_id": d["tool_id"], "quantity": 1}]}).json()
    assert client.delete(f"/api/v1/deleteloanrequest/{req['id']}").status_code == 204
    assert client.get(f"/api/v1/getloanrequest/{req['id']}").status_code == 404
