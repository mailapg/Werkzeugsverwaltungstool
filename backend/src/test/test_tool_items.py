"""Tests for tool items endpoints."""
from src.test.conftest import seed_lookup_data, create_tool, create_tool_item

def test_create_tool_item(client):
    ids = seed_lookup_data(client)
    tool = create_tool(client, ids["category_id"])
    r = client.post("/api/v1/createtoolitem", json={"inventory_no": "INV-001","tool_id": tool["id"],"status_id": ids["status_id"],"condition_id": ids["condition_id"]})
    assert r.status_code == 201
    data = r.json()
    assert data["inventory_no"] == "INV-001"
    assert data["status"]["name"] == "AVAILABLE"
    assert data["condition"]["name"] == "OK"

def test_get_tool_items_list(client):
    ids = seed_lookup_data(client)
    tool = create_tool(client, ids["category_id"])
    create_tool_item(client, tool["id"], ids["status_id"], ids["condition_id"])
    r = client.get("/api/v1/gettoolitems")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_get_tool_item_by_id(client):
    ids = seed_lookup_data(client)
    tool = create_tool(client, ids["category_id"])
    item = create_tool_item(client, tool["id"], ids["status_id"], ids["condition_id"])
    r = client.get(f"/api/v1/gettoolitem/{item['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == item["id"]

def test_get_tool_item_not_found(client):
    assert client.get("/api/v1/gettoolitem/9999").status_code == 404

def test_update_tool_item(client):
    ids = seed_lookup_data(client)
    tool = create_tool(client, ids["category_id"])
    item = create_tool_item(client, tool["id"], ids["status_id"], ids["condition_id"])
    r = client.patch(f"/api/v1/updatetoolitem/{item['id']}", json={"inventory_no": "INV-999"})
    assert r.status_code == 200
    assert r.json()["inventory_no"] == "INV-999"

def test_delete_tool_item(client):
    ids = seed_lookup_data(client)
    tool = create_tool(client, ids["category_id"])
    item = create_tool_item(client, tool["id"], ids["status_id"], ids["condition_id"])
    assert client.delete(f"/api/v1/deletetoolitem/{item['id']}").status_code == 204
    assert client.get(f"/api/v1/gettoolitem/{item['id']}").status_code == 404
