"""Tests for tool item issues endpoints."""
from src.test.conftest import seed_lookup_data, create_tool, create_tool_item, create_user

def _create_issue(client, tool_item_id, user_id, status_id):
    r = client.post("/api/v1/createtoolitemissue", json={"tool_item_id": tool_item_id,"reported_by_user_id": user_id,"status_id": status_id,"title": "Handle broken","description": "The handle is broken."})
    assert r.status_code == 201
    return r.json()

def _setup(client, db):
    from src.app.models.tool_item_issue_status import ToolItemIssueStatus
    ids = seed_lookup_data(client)
    tool = create_tool(client, ids["category_id"])
    item = create_tool_item(client, tool["id"], ids["status_id"], ids["condition_id"])
    user = create_user(client, ids["role_id"], ids["department_id"])
    s = ToolItemIssueStatus(name="OPEN")
    db.add(s); db.commit(); db.refresh(s)
    return {"item_id": item["id"], "user_id": user["id"], "status_id": s.id}

def test_create_tool_item_issue(client, db):
    d = _setup(client, db)
    issue = _create_issue(client, d["item_id"], d["user_id"], d["status_id"])
    assert issue["title"] == "Handle broken"
    assert issue["resolved_at"] is None

def test_get_issues_list(client, db):
    d = _setup(client, db)
    _create_issue(client, d["item_id"], d["user_id"], d["status_id"])
    r = client.get("/api/v1/gettoolitemissues")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_get_tool_item_issue_by_id(client, db):
    d = _setup(client, db)
    issue = _create_issue(client, d["item_id"], d["user_id"], d["status_id"])
    r = client.get(f"/api/v1/gettoolitemissue/{issue['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == issue["id"]

def test_resolve_issue(client, db):
    d = _setup(client, db)
    issue = _create_issue(client, d["item_id"], d["user_id"], d["status_id"])
    r = client.patch(f"/api/v1/resolvetoolitemissue/{issue['id']}")
    assert r.status_code == 200
    assert r.json()["resolved_at"] is not None

def test_get_issue_not_found(client):
    assert client.get("/api/v1/gettoolitemissue/9999").status_code == 404

def test_delete_issue(client, db):
    d = _setup(client, db)
    issue = _create_issue(client, d["item_id"], d["user_id"], d["status_id"])
    assert client.delete(f"/api/v1/deletetoolitemissue/{issue['id']}").status_code == 200
    assert client.get(f"/api/v1/gettoolitemissue/{issue['id']}").status_code == 404
