import pytest
from app import app, db
from models.user import User
from models.item import Item
import bcrypt
import jwt
import os


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["RATELIMIT_ENABLED"] = False

    with app.app_context():
        db.engine.dispose()
        db.create_all()
        with app.test_client() as client:
            yield client
        db.session.remove()
        db.drop_all()


@pytest.fixture
def auth_client(client):
    """
    registers a user and returns client + access token
    reusable fixture — any test that needs a logged in user uses this
    """
    data = {
        "name": "Test User",
        "email": "test@test.com",
        "password": "test1234",
        "phone": "9999999999",
        "department": "CSE"
    }
    response = client.post("/api/auth/register", json=data)
    token = response.get_json()["access_token"]
    return client, token


def test_get_items_empty(client):
    # no items in database — should return empty list
    response = client.get("/api/items/")
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data["items"] == []
    assert json_data["total"] == 0


def test_create_item_success(auth_client):
    client, token = auth_client

    response = client.post("/api/items/", data={
        "title": "Black Wallet",
        "description": "Found near library entrance",
        "category": "Accessories",
        "status": "found",
        "location": "Main Library"
    }, headers={"Authorization": f"Bearer {token}"})

    json_data = response.get_json()

    assert response.status_code == 201
    assert json_data["message"] == "Item posted successfully"
    assert json_data["item"]["title"] == "Black Wallet"


def test_create_item_no_token(client):
    # should fail without token
    response = client.post("/api/items/", data={
        "title": "Black Wallet",
        "description": "Found near library entrance",
        "category": "Accessories",
        "status": "found",
        "location": "Main Library"
    })

    assert response.status_code == 401


def test_create_item_invalid_status(auth_client):
    client, token = auth_client

    response = client.post("/api/items/", data={
        "title": "Black Wallet",
        "description": "Found near library entrance",
        "category": "Accessories",
        "status": "stolen",           # invalid — only lost or found allowed
        "location": "Main Library"
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 400


def test_get_single_item(auth_client):
    client, token = auth_client

    # create item first
    client.post("/api/items/", data={
        "title": "Black Wallet",
        "description": "Found near library entrance",
        "category": "Accessories",
        "status": "found",
        "location": "Main Library"
    }, headers={"Authorization": f"Bearer {token}"})

    # get the item
    response = client.get("/api/items/1")
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data["title"] == "Black Wallet"


def test_get_item_not_found(client):
    response = client.get("/api/items/999")
    assert response.status_code == 404