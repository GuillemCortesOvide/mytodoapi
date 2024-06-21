import os
import sqlite3

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./tests/data/my_test_todo.db")


def get_test_db():
    # Get the test database URL from the environment variable
    db_url = os.getenv("TEST_DATABASE_URL",
                       "sqlite:///C:/Users/guillem.cortes/PycharmProjects/mytodoapi/tests/data/my_test_todo.db")

    # Remove 'sqlite:///' prefix to get the actual file path
    db_path = db_url.replace("sqlite:///", "")

    try:
        connection = sqlite3.connect(db_path)
        return connection
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
