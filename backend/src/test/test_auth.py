"""Tests for the /auth/login endpoint and JWT-protected routes."""
import os
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
import src.app.models  # noqa: F401

# Separate in-memory engine so auth tests are fully isolated
_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


@pytest.fixture()
def auth_db():
    Base.metadata.create_all(bind=_engine)
    session = _Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=_engine)


@pytest.fixture()
def auth_client(auth_db):
    """TestClient WITHOUT auth override – tests the real JWT flow."""
    def override_get_db():
        try:
            yield auth_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    # do NOT override get_current_user here
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _seed_admin(auth_db) -> dict:
    """Creates roles, a department and one ADMIN user directly in the DB."""
    from passlib.context import CryptContext
    from src.app.models.role import Role
    from src.app.models.department import Department
    from src.app.models.user import User

    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    role = Role(name="ADMIN")
    auth_db.add(role)
    auth_db.flush()

    dept = Department(name="IT")
    auth_db.add(dept)
    auth_db.flush()

    user = User(
        firstname="Admin",
        lastname="User",
        email="admin@example.com",
        passwordhash=pwd.hash("Admin123!"),
        role_id=role.id,
        department_id=dept.id,
        is_active=True,
    )
    auth_db.add(user)
    auth_db.commit()
    return {"email": "admin@example.com", "password": "Admin123!", "role_id": role.id, "dept_id": dept.id}


# ---------------------------------------------------------------------------
# Login tests
# ---------------------------------------------------------------------------

def test_login_success(auth_client, auth_db):
    _seed_admin(auth_db)
    r = auth_client.post("/auth/login", data={"username": "admin@example.com", "password": "Admin123!"})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password(auth_client, auth_db):
    _seed_admin(auth_db)
    r = auth_client.post("/auth/login", data={"username": "admin@example.com", "password": "wrong"})
    assert r.status_code == 401


def test_login_unknown_email(auth_client, auth_db):
    r = auth_client.post("/auth/login", data={"username": "nobody@example.com", "password": "x"})
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# Protected route tests
# ---------------------------------------------------------------------------

def test_protected_route_without_token(auth_client, auth_db):
    """GET /api/v1/getusers requires a valid token."""
    r = auth_client.get("/api/v1/getusers")
    assert r.status_code == 401


def test_protected_route_with_token(auth_client, auth_db):
    """GET /api/v1/getusers succeeds with a valid Bearer token."""
    _seed_admin(auth_db)
    login = auth_client.post("/auth/login", data={"username": "admin@example.com", "password": "Admin123!"})
    token = login.json()["access_token"]
    r = auth_client.get("/api/v1/getusers", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200


def test_create_user_requires_admin(auth_client, auth_db):
    """POST /api/v1/createuser with no token returns 401."""
    r = auth_client.post("/api/v1/createuser", json={
        "firstname": "X", "lastname": "Y", "email": "x@y.com",
        "password": "Abc123!", "role_id": 1, "department_id": 1,
    })
    assert r.status_code == 401


def test_admin_can_create_user(auth_client, auth_db):
    """ADMIN can create a new user via POST /api/v1/createuser."""
    creds = _seed_admin(auth_db)
    login = auth_client.post("/auth/login", data={"username": creds["email"], "password": creds["password"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = auth_client.post("/api/v1/createuser", json={
        "firstname": "Hans",
        "lastname": "Maier",
        "email": "hans@example.com",
        "password": "Test123!",
        "role_id": creds["role_id"],
        "department_id": creds["dept_id"],
    }, headers=headers)
    assert r.status_code == 201
    assert r.json()["email"] == "hans@example.com"


# ---------------------------------------------------------------------------
# Logout tests
# ---------------------------------------------------------------------------

def test_logout_success(auth_client, auth_db):
    """POST /auth/logout invalidates the token (204)."""
    _seed_admin(auth_db)
    login = auth_client.post("/auth/login", data={"username": "admin@example.com", "password": "Admin123!"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = auth_client.post("/auth/logout", headers=headers)
    assert r.status_code == 204


def test_logout_token_rejected_afterwards(auth_client, auth_db):
    """After logout the same token must be rejected with 401."""
    _seed_admin(auth_db)
    login = auth_client.post("/auth/login", data={"username": "admin@example.com", "password": "Admin123!"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    auth_client.post("/auth/logout", headers=headers)

    r = auth_client.get("/api/v1/getusers", headers=headers)
    assert r.status_code == 401


def test_logout_without_token(auth_client, auth_db):
    """POST /auth/logout without token returns 401."""
    r = auth_client.post("/auth/logout")
    assert r.status_code == 401
