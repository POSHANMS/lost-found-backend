import pytest
from app import app, db
from models.user import User
from models.item import Item
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
        db.drop_all()


def register_and_login(client, email="test@test.com"):
    """helper function — registers and returns token"""
    data = {
        "name": "Test User",
        "email": email,
        "password": "test1234",
        "phone": "9999999999",
        "department": "CSE"
    }
    response = client.post("/api/auth/register", json=data)
    return response.get_json()["access_token"]


def create_item(client, token):
    """helper function — creates item and returns response"""
    return client.post("/api/items/", data={
        "title": "Black Wallet",
        "description": "Found near library entrance",
        "category": "Accessories",
        "status": "found",
        "location": "Main Library"
    }, headers={"Authorization": f"Bearer {token}"})


def test_make_claim_success(client):
    # two different users needed — one posts item, another claims it
    token1 = register_and_login(client, "owner@test.com")
    token2 = register_and_login(client, "claimant@test.com")

    # owner posts item
    create_item(client, token1)

    # claimant makes claim
    response = client.post("/api/claims/1", json={
        "message": "This is my wallet, it has my ID inside"
    }, headers={"Authorization": f"Bearer {token2}"})

    assert response.status_code == 201
    assert response.get_json()["message"] == "Claim submitted successfully"


def test_claim_own_item(client):
    # user cannot claim their own item
    token = register_and_login(client)
    create_item(client, token)

    response = client.post("/api/claims/1", json={
        "message": "This is my wallet, it has my ID inside"
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 400


def test_duplicate_claim(client):
    token1 = register_and_login(client, "owner@test.com")
    token2 = register_and_login(client, "claimant@test.com")

    create_item(client, token1)

    # first claim
    client.post("/api/claims/1", json={
        "message": "This is my wallet, it has my ID inside"
    }, headers={"Authorization": f"Bearer {token2}"})

    # second claim — should fail
    response = client.post("/api/claims/1", json={
        "message": "This is my wallet, it has my ID inside"
    }, headers={"Authorization": f"Bearer {token2}"})

    assert response.status_code == 409


def test_claim_nonexistent_item(client):
    token = register_and_login(client, "unique@test.com")

    response = client.post("/api/claims/999", json={
        "message": "This is my wallet, it has my ID inside"
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404


def test_claim_no_token(client):
    response = client.post("/api/claims/1", json={
        "message": "This is my wallet"
    })
    assert response.status_code == 401