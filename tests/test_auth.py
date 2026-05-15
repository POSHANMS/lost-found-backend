import pytest
from app import app, db
from models.user import User
from flask_limiter import Limiter
import bcrypt


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["RATELIMIT_ENABLED"] = False
    app.config["RATELIMIT_STORAGE_URI"] = "memory://"

    with app.app_context():
        db.engine.dispose()
        db.create_all()
        with app.test_client() as client:
            yield client
        db.session.remove()
        db.drop_all()# drop SQLite tables (not Supabase)


def test_register_success(client):
    data = {
        "name": "Test User",
        "email": "test@test.com",
        "password": "test1234",
        "phone": "9999999999",
        "department": "CSE"
    }
    response = client.post("/api/auth/register", json=data)
    json_data = response.get_json()

    assert response.status_code == 201
    assert json_data["message"] == "Registration successful"
    assert "access_token" in json_data


def test_register_duplicate_email(client):
    data = {
        "name": "Test User",
        "email": "test@test.com",
        "password": "test1234",
        "phone": "9999999999",
        "department": "CSE"
    }
    client.post("/api/auth/register", json=data)
    response = client.post("/api/auth/register", json=data)
    json_data = response.get_json()

    assert response.status_code == 409
    assert "error" in json_data


def test_login_success(client):
    # Arrange — register first then login
    data = {
        "name": "Test User",
        "email": "test@test.com",
        "password": "test1234",
        "phone": "9999999999",
        "department": "CSE"
    }
    client.post("/api/auth/register", json=data)

    # Act
    response = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "test1234"
    })
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data["message"] == "Login successful"
    assert "access_token" in json_data


def test_login_wrong_password(client):
    data = {
        "name": "Test User",
        "email": "test@test.com",
        "password": "test1234",
        "phone": "9999999999",
        "department": "CSE"
    }
    client.post("/api/auth/register", json=data)

    response = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401


def test_login_missing_fields(client):
    response = client.post("/api/auth/login", json={})
    assert response.status_code == 400