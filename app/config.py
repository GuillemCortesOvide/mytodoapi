import os
import sqlite3

# Default database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/my_todo.db")

# Default test database URL
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./data/my_test_todo.db")


def get_test_db():
    db_url = os.getenv("TEST_DATABASE_URL", "sqlite:///./data/my_test_todo.db")
    connection = sqlite3.connect(db_url.replace("sqlite:///", ""))
    return connection
