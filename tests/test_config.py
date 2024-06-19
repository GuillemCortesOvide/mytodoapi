import os
import sqlite3


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./tests/data/my_test_todo.db")


def get_test_db():
    db_url = os.getenv("TEST_DATABASE_URL", "sqlite:///./tests/data/my_test_todo.db")
    connection = sqlite3.connect(db_url.replace("sqlite:///", ""))
    return connection
