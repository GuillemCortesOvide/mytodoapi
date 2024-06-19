import hashlib
import sqlite3
import os
from app.config import DATABASE_URL, TEST_DATABASE_URL


def get_db():
    db_url = os.getenv("DATABASE_URL", DATABASE_URL)
    connection = sqlite3.connect(db_url.split(":///./")[1])
    cursor = connection.cursor()
    try:
        yield cursor
    finally:
        connection.commit()
        connection.close()


def hash_password(password: str) -> str:
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(password.encode('utf-8'))
    hashed_password = hash_algorithm.hexdigest()
    return hashed_password


def initialize_db():
    db_url = os.getenv("DATABASE_URL", DATABASE_URL)
    connection = sqlite3.connect(db_url.split(":///./")[1])
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todo_lists (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todo_items (
            id INTEGER PRIMARY KEY,
            list_id INTEGER NOT NULL,
            context TEXT NOT NULL,
            completed BOOLEAN NOT NULL,
            FOREIGN KEY (list_id) REFERENCES todo_lists (id)
        );
    """)
    connection.commit()
    connection.close()


def initialize_test_db():
    db_url = os.getenv("TEST_DATABASE_URL", TEST_DATABASE_URL)
    connection = sqlite3.connect(db_url.split(":///./")[1])
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todo_lists (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todo_items (
            id INTEGER PRIMARY KEY,
            list_id INTEGER NOT NULL,
            context TEXT NOT NULL,
            completed BOOLEAN NOT NULL,
            FOREIGN KEY (list_id) REFERENCES todo_lists (id)
        );
    """)
    connection.commit()
    connection.close()
