import sqlite3
from urllib import response
from fastapi.testclient import TestClient
from app.main import app, my_db
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
        "context": f"Test task: {unique_id}",
        "completed": 0
    }

def test_db_session():
    connection = sqlite3.connect("my_test_todo.db")
    cursor = connection.cursor()
    try:
        return cursor
    finally:
        connection.cursor()
        connection.close()


# User Realm Tests ---------------------------------


def test_create_user(get_sample_user):
    user_response = client.post("/users", json=get_sample_user)

    try:
        assert user_response.status_code == 201
       
    except Exception as e:
        print(f"Test failed: {e}")
        raise


def test_delete_user(get_sample_user):
    # Create a user first
    create_response = client.post("/users", json=get_sample_user)

    try:
        assert create_response.status_code == 201
    except AssertionError as e:
        print(f"Assertion error: {e}")
        print(f"Response content: {create_response.content}")
        raise

    # Get the user_id from the created user
    user_id = create_response.json().get("user_id")

    # Print the response content
    print(f"Response content: {create_response.json()}")

    # Ensure that user_id is a valid integer
    assert isinstance(user_id, int), f"Invalid user_id: {user_id}"

    # Delete the user with the correct URL
    delete_response = client.delete(f"/users/{user_id}")

    try:
        assert delete_response.status_code == 200
    except AssertionError as e:
        print(f"Assertion error: {e}")
        print(f"Response content: {delete_response.content}")
        raise


def test_get_users(get_sample_user):
    get_response = client.get("/users")
    assert get_response.status_code == 200, (f"Expected status code 200, but got {get_response.status_code}"
                                             f". Response content: {get_response.content}")
    assert "users" in get_response.json()


def test_update_user(get_sample_user):
    # Create a user first
    response_create = client.post("/users", json=get_sample_user)
    try:
        assert response_create.status_code == 201

        user_id = response_create.json()["user_id"]

        # Update the user with new data

        updated_data = get_sample_user

        response_update = client.put(f"/users/{user_id}", json=updated_data)
        assert response_update.status_code == 201, (f"Expected status code 200, but got {response.status_code}"
                                                    f". Response content: {response.content}")
    except Exception as e:
        print(f"Test failed: {e}")
        raise


# Lists Realm Tests ---------------------------------


def test_create_list(get_sample_list, get_sample_user):
    # Create a user first
    create_user_response = client.post("/users", json=get_sample_user)
    print(f"Create User Response: {create_user_response.content}")
    assert create_user_response.status_code == 201

    # Extract the user_id from the created user
    user_id = create_user_response.json().get("user_id")

    # Create a to-do list for the user
    list_response = client.post(f"/todo-lists/{user_id}", json=get_sample_list)
    print(f"Create List Response: {list_response.content}")

    try:
        assert list_response.status_code == 201
    except Exception as e:
        print(f"Test failed: {e}")
        raise


def test_delete_list(get_sample_user):
    # Create a user first
    create_response = client.post("/users", json=get_sample_user)

    try:
        assert create_response.status_code == 201
    except AssertionError as e:
        print(f"Assertion error: {e}")
        print(f"Response content: {create_response.content}")
        raise

    # Get the user_id from the created user
    user_id = create_response.json().get("user_id")

    # Delete the user
    delete_response = client.delete(f"/users/{user_id}")

    try:
        assert delete_response.status_code == 200
    except AssertionError as e:
        print(f"Assertion error: {e}")
        print(f"Response content: {delete_response.content}")
        raise

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


def test_update_list(get_sample_user):
    # Create a user first
    response_create = client.post("/users", json=get_sample_user)
    try:
        assert response_create.status_code == 201

        user_id = response_create.json()["user_id"]

        # Update the user with new data

        updated_data = get_sample_user

        response_update = client.put(f"/users/{user_id}", json=updated_data)
        assert response_update.status_code == 201, (f"Expected status code 200, but got {response.status_code}"
                                                    f". Response content: {response.content}")
    except Exception as e:
        print(f"Test failed: {e}")
        raise


# Tasks Realm Tests ---------------------------------


def test_create_task(get_sample_user, get_sample_list, get_sample_task):
    # Create a user
    user_response = client.post("/users", json=get_sample_user)

    try:
        assert user_response.status_code == 201
    except AssertionError as e:
        print(f"User creation failed: {e}")
        print(f"Response content: {user_response.content}")
        raise

    # Get the user_id from the created user
    user_id = user_response.json().get("user_id")

    # Create a list for the user
    list_response = client.post(f"/todo-lists/{user_id}", json=get_sample_list)

    try:
        assert list_response.status_code == 201
    except AssertionError as e:
        print(f"List creation failed: {e}")
        print(f"Response content: {list_response.content}")
        raise

    # Get the list_id from the created list
    list_id = list_response.json().get("list_id")

    # Create a task for the list
    task_response = client.post(f"/todo-items/{list_id}/{user_id}", json=get_sample_task)

    try:
        assert task_response.status_code == 201
    except AssertionError as e:
        print(f"Task creation failed: {e}")
        print(f"Response content: {task_response.content}")
        raise



def test_delete_task(get_sample_user):
    # Create a user first
    create_response = client.post("/users", json=get_sample_user)

    try:
        assert create_response.status_code == 201
    except AssertionError as e:
        print(f"Assertion error: {e}")
        print(f"Response content: {create_response.content}")
        raise

    # Get the user_id from the created user
    user_id = create_response.json().get("user_id")

    # Delete the user
    delete_response = client.delete(f"/users/{user_id}")

    try:
        assert delete_response.status_code == 200
    except AssertionError as e:
        print(f"Assertion error: {e}")
        print(f"Response content: {delete_response.content}")
        raise

    # Request to get the deleted user and assert that it's not found
    response_get_deleted = client.get(f"/users/{user_id}")
    assert response_get_deleted.status_code == 404


def test_get_tasks():
    response = client.get("/users")
    assert response.status_code == 200, (f"Expected status code 200, but got {response.status_code}"
                                         f". Response content: {response.content}")
    assert "users" in response.json()


def test_update_task(get_sample_user):
    # Create a user first
    response_create = client.post("/users", json=get_sample_user)
    try:
        assert response_create.status_code == 201

        user_id = response_create.json()["user_id"]

        # Update the user with new data

        updated_data = get_sample_user

        response_update = client.put(f"/users/{user_id}", json=updated_data)
        assert response_update.status_code == 201, (f"Expected status code 200, but got {response.status_code}"
                                                    f". Response content: {response.content}")
    except Exception as e:
        print(f"Test failed: {e}")
        raise
