import pytest
from app import app, db
from models.user import User
import bcrypt

@pytest.fixture
def client():
    """
    fixture = reusable setup for tests
    this creates a test version of the app with a separate test database
    runs before every test function automatically
    """
    app.config["TESTING"]=True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"     # temporary in-memory database
    app.config["RATELIMIT_ENABLED"] = False     # disable rate limiting in tests

    with app.test_client() as client:
        with app.app_context():
            db.create_all()         # create tables in test database
            yield client            # run the test
            db.drop_all()           # clean up after test


def test_register_success(client):
    # Arrange
    data = {
        "name": "Test User",
        "email": "test@test.com",
        "password": "test1234",
        "phone": "9999999999",
        "department": "CSE"
    }

    # Act
    response = client.post("/api/auth/register", json=data)
    json_data = response.get_json()

    # Assert
    assert response.status_code == 201
    assert json_data["message"] == "Registration successful"
    assert "access_token" in json_data

def test_register_duplicate_email(client):
    # Arrange — register once first
    data = {
        "name": "Test User",
        "email": "test@test.com",
        "password": "test1234",
        "phone": "9999999999",
        "department": "CSE"
    }
    client.post("/api/auth/register", json=data)

    # Act — try to register again with same email
    response = client.post("/api/auth/register", json=data)
    json_data = response.get_json()

    # Assert
    assert response.status_code == 409
    assert "error" in json_data


def test_login_success(client):
    # Arrange — create user manually in test database
    with app.app_context():
        hashed = bcrypt.hashpw("test1234".encode(), bcrypt.gensalt()).decode()
        user = User(
            name="Test User",
            email="test@test.com",
            password=hashed,
            phone="9999999999",
            department="CSE"
        )
        db.session.add(user)
        db.session.commit()

        # Act

        response = client.post("/api/auth/login", json={
            "email": "test@test.com",
            "password": "test1234"
        })
        json_data = response.get_json()

        # Assert
        assert response.status_code == 200
        assert json_data["message"] == "Login successful"
        assert "access_token" in json_data


def test_login_wrong_password(client):
    # Arrange
    with app.app_context():
        hashed = bcrypt.hashpw("test1234".encode(), bcrypt.gensalt()).decode()
        user = User(
            name="Test User",
            email="test@test.com",
            password=hashed,
            phone="9999999999",
            department="CSE"
        )
        db.session.add(user)
        db.session.commit()

    # Act
    response = client.post("/api/auth/login", json={
        "email": "test@test.com",
        "password": "wrongpassword"
    })

    # Assert
    assert response.status_code == 401

def test_login_missing_fields(client):
    # Act — send empty body
    response = client.post("/api/auth/login", json={})

    # Assert
    assert response.status_code == 400
