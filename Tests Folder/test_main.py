import sqlite3
from fastapi.testclient import TestClient
from app.main import app
import pytest
import uuid

client = TestClient(app)


@pytest.fixture
def get_sample_user():
    unique_id = str(uuid.uuid4())[:8]
    return {
        "username": f"test_user_{unique_id}",
        "email": f"test@{unique_id}.com",
        "password": f"{unique_id}test-password"
    }


@pytest.fixture
def get_sample_list():
    unique_id = str(uuid.uuid4())[:8]
    return {
        "title": f"List of test {unique_id}"
    }


@pytest.fixture
def get_sample_task():
    unique_id = str(uuid.uuid4())[:8]
    return {
        "completed": "0",
        "context": f"Test task: {unique_id}"
    }


def test_db_session():
    connection = sqlite3.connect("data/my_test_todo.db")
    cursor = connection.cursor()
    try:
        return cursor
    finally:
        connection.cursor()
        connection.close()


# User Realm Tests ---------------------------------


def test_create_user(get_sample_user):
    user_response = client.post("/users", json=get_sample_user)

    assert user_response.status_code == 201


def test_delete_user(get_sample_user):
    # Create a user first
    create_response = client.post("/users", json=get_sample_user)

    assert create_response.status_code == 201

    # Get the user_id from the created user
    user_id = create_response.json().get("user_id")

    # Ensure that user_id is a valid integer
    assert isinstance(user_id, int), f"Invalid user_id: {user_id}"

    # Delete the user with the correct URL
    delete_response = client.delete(f"/users/{user_id}")

    assert delete_response.status_code == 200


def test_get_users(get_sample_user):
    get_response = client.get("/users")
    assert get_response.status_code == 200

    assert "users" in get_response.json()


def test_update_user(get_sample_user):
    # Create a user first
    response_create = client.post("/users", json=get_sample_user)

    assert response_create.status_code == 201

    user_id = response_create.json()["user_id"]

    # Update the user with new data

    updated_data = get_sample_user

    response_update = client.put(f"/users/{user_id}", json=updated_data)
    assert response_update.status_code == 201


# Lists Realm Tests ---------------------------------


def test_create_list(get_sample_list, get_sample_user):
    # Create a user first
    create_user_response = client.post("/users", json=get_sample_user)
    assert create_user_response.status_code == 201

    # Extract the user_id from the created user
    user_id = create_user_response.json().get("user_id")

    # Create a to-do list for the user
    list_response = client.post(f"/todo-lists/{user_id}", json=get_sample_list)
    assert list_response.status_code == 201


def test_delete_list(get_sample_user):
    # Create a user first
    create_response = client.post("/users", json=get_sample_user)
    assert create_response.status_code == 201

    # Get the user_id from the created user
    user_id = create_response.json().get("user_id")

    # Delete the user
    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 200

    # Request to get the deleted user and assert that it's not found
    response_get_deleted = client.get(f"/users/{user_id}")
    assert response_get_deleted.status_code == 404


def test_get_lists():
    list_response = client.get("/todo-lists")
    assert list_response.status_code == 200, (
        f"Expected status code 200, but got {list_response.status_code}. Response content: {list_response.content}"
    )
    assert "todo_lists" in list_response.json()
    todo_lists = list_response.json()["todo_lists"]
    assert isinstance(todo_lists, list)


def test_update_list(get_sample_user, get_sample_list):
    # Create a user
    user_response = client.post("/users", json=get_sample_user)
    assert user_response.status_code == 201

    # Get the user_id from the created user
    user_id = user_response.json().get("user_id")

    # Create a list for the user
    list_response = client.post(f"/todo-lists/{user_id}", json=get_sample_list)
    assert list_response.status_code == 201

    # Get the list_id from the created list
    list_id = list_response.json().get("list_id")

    updated_data = get_sample_list

    list_update = client.put(f"/todo-lists/{list_id}", json=updated_data)
    assert list_update.status_code == 201


# Tasks Realm Tests ---------------------------------

def test_create_task(get_sample_user, get_sample_list, get_sample_task):
    # Create a user
    user_response = client.post("/users", json=get_sample_user)
    assert user_response.status_code == 201

    # Get the user_id from the created user
    user_id = user_response.json().get("user_id")

    # Create a list for the user
    list_response = client.post(f"/todo-lists/{user_id}", json=get_sample_list)
    assert list_response.status_code == 201

    # Get the list_id from the created list
    list_id = list_response.json().get("list_id")

    # Create a task for the list
    task_response = client.post(f"/todo-items/{list_id}/{user_id}", json=get_sample_task)
    assert task_response.status_code == 201


def test_delete_task(get_sample_user):
    # Create a task first
    create_response = client.post("/users", json=get_sample_user)

    assert create_response.status_code == 201

    # Get the user_id from the created user
    user_id = create_response.json().get("user_id")

    # Delete the user
    delete_response = client.delete(f"/users/{user_id}")

    assert delete_response.status_code == 200

    # Request to get the deleted user and assert that it's not found
    response_get_deleted = client.get(f"/users/{user_id}")
    assert response_get_deleted.status_code == 404


def test_get_tasks():
    response = client.get("/todo-items")
    assert response.status_code == 200, (f"Expected status code 200, but got {response.status_code}"
                                         f". Response content: {response.content}")


def test_update_task(get_sample_user, get_sample_list, get_sample_task):
    # Create a user
    user_response = client.post("/users", json=get_sample_user)
    assert user_response.status_code == 201

    # Get the user_id from the created user
    user_id = user_response.json().get("user_id")

    # Create a list for the user
    list_response = client.post(f"/todo-lists/{user_id}", json=get_sample_list)
    assert list_response.status_code == 201

    # Get the list_id from the created list
    list_id = list_response.json().get("list_id")

    # Create a task for the list
    task_response = client.post(f"/todo-items/{list_id}/{user_id}", json=get_sample_task)
    assert task_response.status_code == 201

    updated_data = get_sample_task

    task_update = client.put(f"/todo-items/{list_id}", json=updated_data)
    assert task_update.status_code == 201
