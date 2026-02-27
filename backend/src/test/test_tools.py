from io import BytesIO

from src.test.conftest import create_tool_category, create_tool

def test_create_tool_category(client):
    r = client.post("/api/v1/createtoolcategory", json={"name": "Hand Tools"})
    assert r.status_code == 201
    assert r.json()["name"] == "Hand Tools"

def test_get_tool_categories(client):
    create_tool_category(client, "Category A")
    r = client.get("/api/v1/gettoolcategories")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_get_tool_category_by_id(client):
    cat = create_tool_category(client, "Power Tools")
    r = client.get(f"/api/v1/gettoolcategory/{cat['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "Power Tools"

def test_get_tool_category_not_found(client):
    assert client.get("/api/v1/gettoolcategory/9999").status_code == 404

def test_update_tool_category(client):
    cat = create_tool_category(client, "Old")
    r = client.patch(f"/api/v1/updatetoolcategory/{cat['id']}", json={"name": "New"})
    assert r.status_code == 200
    assert r.json()["name"] == "New"

def test_delete_tool_category(client):
    cat = create_tool_category(client, "Temp")
    assert client.delete(f"/api/v1/deletetoolcategory/{cat['id']}").status_code == 200
    assert client.get(f"/api/v1/gettoolcategory/{cat['id']}").status_code == 404

def test_create_tool(client):
    cat = create_tool_category(client)
    r = client.post("/api/v1/createtool", data={"tool_name": "Hammer", "description": "Claw hammer", "category_id": cat["id"]})
    assert r.status_code == 201
    assert r.json()["tool_name"] == "Hammer"
    assert r.json()["category"]["id"] == cat["id"]

def test_get_tools_list(client):
    cat = create_tool_category(client)
    create_tool(client, cat["id"], "Saw")
    r = client.get("/api/v1/gettools")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_get_tool_by_id(client):
    cat = create_tool_category(client)
    tool = create_tool(client, cat["id"], "Screwdriver")
    r = client.get(f"/api/v1/gettool/{tool['id']}")
    assert r.status_code == 200
    assert r.json()["tool_name"] == "Screwdriver"

def test_get_tool_not_found(client):
    assert client.get("/api/v1/gettool/9999").status_code == 404

def test_update_tool(client):
    cat = create_tool_category(client)
    tool = create_tool(client, cat["id"])
    r = client.patch(f"/api/v1/updatetool/{tool['id']}", data={"tool_name": "Big Hammer"})
    assert r.status_code == 200
    assert r.json()["tool_name"] == "Big Hammer"

def test_delete_tool(client):
    cat = create_tool_category(client)
    tool = create_tool(client, cat["id"])
    assert client.delete(f"/api/v1/deletetool/{tool['id']}").status_code == 200
    assert client.get(f"/api/v1/gettool/{tool['id']}").status_code == 404


def test_create_tool_with_image(client):
    cat = create_tool_category(client)
    fake_image = BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
    r = client.post(
        "/api/v1/createtool",
        data={"tool_name": "Hammer", "category_id": cat["id"]},
        files={"image": ("tool.png", fake_image, "image/png")},
    )
    assert r.status_code == 201
    assert r.json()["image_filename"] is not None


def test_upload_tool_image(client):
    cat = create_tool_category(client)
    tool = create_tool(client, cat["id"])
    fake_image = BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
    r = client.post(
        f"/api/v1/uploadtoolimage/{tool['id']}",
        files={"file": ("test.png", fake_image, "image/png")},
    )
    assert r.status_code == 200
    assert r.json()["image_filename"] is not None


def test_upload_tool_image_invalid_type(client):
    cat = create_tool_category(client)
    tool = create_tool(client, cat["id"])
    r = client.post(
        f"/api/v1/uploadtoolimage/{tool['id']}",
        files={"file": ("test.txt", BytesIO(b"hello"), "text/plain")},
    )
    assert r.status_code == 400


def test_delete_tool_image(client):
    cat = create_tool_category(client)
    tool = create_tool(client, cat["id"])
    fake_image = BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
    client.post(
        f"/api/v1/uploadtoolimage/{tool['id']}",
        files={"file": ("test.png", fake_image, "image/png")},
    )
    assert client.delete(f"/api/v1/deletetoolimage/{tool['id']}").status_code == 200
    r = client.get(f"/api/v1/gettool/{tool['id']}")
    assert r.json()["image_filename"] is None
