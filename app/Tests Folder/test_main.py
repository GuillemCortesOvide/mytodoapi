import sqlite3
from urllib import response
from fastapi.testclient import TestClient
from app.main import app
import pytest
import logging

logging.basicConfig(level=logging.DEBUG)
client = TestClient(app)


@pytest.fixture
def sample_user():
    return {
        "username": "test_user",
        "email": "test@myexample.com",
        "password": "test-password"
    }


def test_db_session():
    connection = sqlite3.connect("my_test_todo.db")
    cursor = connection.cursor()
    try:
        return cursor
    finally:
        connection.cursor()
        connection.close()


def test_create_user(sample_user):
    response = client.post("/users", json=sample_user)

    try:
        assert response.status_code == 201

    except Exception as e:
        # Print additional information or raise a custom assertion error
        print(f"Test failed: {e}")
        raise


def test_delete_user(sample_user):
    response_create = client.post("/users", json=sample_user)
    assert response_create.status_code == 201

    user_id = response_create.json()["user_id"]

    response_delete = client.delete(f"/users/{user_id}")

    try:
        assert response_delete.status_code == 200
    except Exception as e:
        # Print additional information or raise a custom assertion error
        print(f"Test failed: {e}")
        print(f"Response content: {response_delete.content}")
        raise

    # request to get the deleted user and assert that it's not found
    response_get_deleted = client.get(f"/users/{user_id}")
    assert response_get_deleted.status_code == 404


def test_get_users():
    response = client.get("/users")
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}. Response content: {response.content}"
    assert "users" in response.json()


def test_update_user(sample_user):
    # Create a user first
    response_create = client.post("/users", json=sample_user)
    assert response_create.status_code == 201

    user_id = response_create.json()["user_id"]

    # Update the user with new data
    updated_data = {
        "username": "new_username",
        "email": "new_email@example.com",
        "password": "new_password"
    }

    response_update = client.put(f"/users/{user_id}", json=updated_data)
    assert response_update.status_code == 201, f"Expected status code 200, but got {response.status_code}. Response content: {response.content}"
