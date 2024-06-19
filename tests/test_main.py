import uuid
import sqlite3
import pytest
from fastapi.testclient import TestClient
from app.main import app
from tests.test_config import get_test_db

client = TestClient(app)


def test_initialize_test_db():
    connection = get_test_db()
    if connection is None:
        pytest.fail("Failed to establish database connection. Check logs for details.")

    try:
        cursor = connection.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username VARCHAR(255) UNIQUE,
                email TEXT,
                password VARCHAR(255)
            );
            CREATE TABLE IF NOT EXISTS todo_lists (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                title TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            CREATE TABLE IF NOT EXISTS todo_items (
                id INTEGER PRIMARY KEY,
                list_id INTEGER,
                context TEXT,
                completed BOOLEAN,
                FOREIGN KEY (list_id) REFERENCES todo_lists (id)
            );
        ''')
        connection.commit()
    except sqlite3.Error as e:
        pytest.fail(f"SQLite error during table creation: {e}")
    finally:
        if connection:
            connection.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    test_initialize_test_db()


@pytest.fixture
def get_sample_user():
    unique_id = str(uuid.uuid4())[:8]
    return {
        "username": f"test_user_{unique_id}",
        "email": f"test@{unique_id}.com",
        "password": f"{unique_id}test-password"
    }


def test_create_user(get_sample_user):
    response = client.post("/users", json=get_sample_user)
    assert response.status_code == 201
    assert response.json().get("user_id") is not None


def test_create_list(get_sample_user, get_sample_list):
    user_response = client.post("/users", json=get_sample_user)
    assert user_response.status_code == 201

    user_id = user_response.json().get("user_id")
    list_response = client.post(f"/todo-lists/{user_id}", json=get_sample_list)
    assert list_response.status_code == 201
    assert list_response.json().get("list_id") is not None


def test_create_task(get_sample_user, get_sample_list, get_sample_task):
    user_response = client.post("/users", json=get_sample_user)
    assert user_response.status_code == 201

    user_id = user_response.json().get("user_id")
    list_response = client.post(f"/todo-lists/{user_id}", json=get_sample_list)
    assert list_response.status_code == 201

    list_id = list_response.json().get("list_id")
    task_response = client.post(f"/todo-items/{list_id}/{user_id}", json=get_sample_task)
    assert task_response.status_code == 201


def test_delete_task(get_sample_user):
    create_response = client.post("/users", json=get_sample_user)
    assert create_response.status_code == 201

    user_id = create_response.json().get("user_id")
    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 200

    response_get_deleted = client.get(f"/users/{user_id}")
    assert response_get_deleted.status_code == 404


def test_get_tasks():
    response = client.get("/todo-items")
    assert response.status_code == 200, (
        f"Expected status code 200, but got {response.status_code}. Response content: {response.content}"
    )


def test_update_task(get_sample_user, get_sample_list, get_sample_task):
    user_response = client.post("/users", json=get_sample_user)
    assert user_response.status_code == 201

    user_id = user_response.json().get("user_id")
    list_response = client.post(f"/todo-lists/{user_id}", json=get_sample_list)
    assert list_response.status_code == 201

    list_id = list_response.json().get("list_id")
    task_response = client.post(f"/todo-items/{list_id}/{user_id}", json=get_sample_task)
    assert task_response.status_code == 201

    updated_data = get_sample_task
    updated_data["completed"] = True

    task_update = client.put(f"/todo-items/{list_id}", json=updated_data)
    assert task_update.status_code == 200
