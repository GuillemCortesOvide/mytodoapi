import hashlib
import sqlite3
from app.main import DATABASE_URL


def get_db():
    with sqlite3.connect(DATABASE_URL) as connection:
        cursor = connection.cursor()
        try:
            yield cursor
        finally:
            connection.commit()


def hash_password(password: str) -> str:
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(password.encode('utf-8'))
    hashed_password = hash_algorithm.hexdigest()

    return hashed_password


def initialize_db():
    with sqlite3.connect(DATABASE_URL) as connection:
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
    initialize_db()
