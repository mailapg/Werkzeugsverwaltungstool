"""
Test configuration for the Werkzeugverwaltungstool.

Each test gets a fresh in-memory SQLite database.
The FastAPI dependency get_db is overridden with a test session.
Auth (get_current_user) is bypassed with a mock ADMIN user so that
existing CRUD tests don't need to send Bearer tokens.
"""
import os

# DATABASE_URL and JWT_SECRET_KEY must be set BEFORE src.app.* is imported,
# because config.py evaluates Settings on import.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("SEED_MANAGER_EMAIL", "seed@test.local")
os.environ.setdefault("SEED_MANAGER_PASSWORD", "Test123!")
os.environ.setdefault("SEED_MANAGER_FIRSTNAME", "Seed")
os.environ.setdefault("SEED_MANAGER_LASTNAME", "User")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.app.db.base import Base
from src.app.db.deps import get_db
from src.app.main import app
import src.app.models  # noqa: F401 – register all models with Base.metadata

# StaticPool ensures all sessions share the same in-memory SQLite connection
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------------------------
# Mock admin user – used to bypass auth in non-auth tests
# ---------------------------------------------------------------------------

class _MockRole:
    name = "ADMIN"


class _MockAdminUser:
    id = 0
    is_active = True
    role = _MockRole()


def _mock_get_current_user():
    return _MockAdminUser()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def db():
    """Creates all tables, yields a session, then cleans up."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    """
    FastAPI TestClient with:
    - overridden DB dependency (in-memory SQLite)
    - overridden get_current_user (mock ADMIN – no token required)
    """
    from src.app.auth.security import get_current_user

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = _mock_get_current_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helper functions: create test data via the API
# ---------------------------------------------------------------------------

def create_role(client: TestClient, name: str = "ADMIN") -> dict:
    r = client.post("/api/v1/createrole", json={"name": name})
    assert r.status_code == 201
    return r.json()


def create_department(client: TestClient, name: str = "Workshop", lead_user_id=None) -> dict:
    r = client.post("/api/v1/createdepartment", json={"name": name, "lead_user_id": lead_user_id})
    assert r.status_code == 201
    return r.json()


def create_user(
    client: TestClient,
    role_id: int,
    department_id: int,
    email: str = "test@firma.local",
) -> dict:
    r = client.post(
        "/api/v1/createuser",
        json={
            "firstname": "Max",
            "lastname": "Mustermann",
            "email": email,
            "password": "Secret123!",
            "role_id": role_id,
            "department_id": department_id,
        },
    )
    assert r.status_code == 201
    return r.json()


def create_tool_category(client: TestClient, name: str = "Hand Tools") -> dict:
    r = client.post("/api/v1/createtoolcategory", json={"name": name})
    assert r.status_code == 201
    return r.json()


def create_tool_status(client: TestClient, name: str = "AVAILABLE") -> dict:
    r = client.post("/api/v1/createtoolstatus", json={"name": name})
    assert r.status_code == 201
    return r.json()


def create_tool_condition(client: TestClient, name: str = "OK") -> dict:
    r = client.post("/api/v1/createtoolcondition", json={"name": name})
    assert r.status_code == 201
    return r.json()


def create_tool(client: TestClient, category_id: int, name: str = "Hammer") -> dict:
    r = client.post(
        "/api/v1/createtool",
        data={"tool_name": name, "description": "Test description", "category_id": category_id},
    )
    assert r.status_code == 201
    return r.json()


def create_tool_item(
    client: TestClient,
    tool_id: int,
    status_id: int,
    condition_id: int,
    inventory_no: str = "INV-001",
) -> dict:
    r = client.post(
        "/api/v1/createtoolitem",
        json={
            "inventory_no": inventory_no,
            "tool_id": tool_id,
            "status_id": status_id,
            "condition_id": condition_id,
        },
    )
    assert r.status_code == 201
    return r.json()


def seed_lookup_data(client: TestClient) -> dict:
    """Creates all required lookup entries and returns their IDs."""
    role = create_role(client, "EMPLOYEE")
    dept = create_department(client, "Workshop")
    ts_available = create_tool_status(client, "AVAILABLE")
    ts_loaned = create_tool_status(client, "LOANED")
    ts_defect = create_tool_status(client, "DEFECT")
    create_tool_status(client, "RETIRED")
    tc = create_tool_condition(client, "OK")
    create_tool_condition(client, "DEFECT")
    cat = create_tool_category(client, "Hand Tools")
    return {
        "role_id": role["id"],
        "department_id": dept["id"],
        "status_id": ts_available["id"],
        "loaned_status_id": ts_loaned["id"],
        "defect_status_id": ts_defect["id"],
        "condition_id": tc["id"],
        "category_id": cat["id"],
    }
