# db_operations.py
from pydantic import BaseModel
import sqlite3

conn = sqlite3.connect('my_todo.db')
cursor = conn.cursor()


class User(BaseModel):
    username: str
    email: str
    password: str


class UserId(BaseModel):
    id: int


def insert_user(user, db):

    try:
        # Insert user into the 'users' table
        new_user = db["users"].insert({
            "username": user.username,
            "email": user.email,
            "password": user.password
        })

        return {"message": "User created successfully"}
    except Exception as e:
        return {"error": str(e)}


def delete_user(user, db):
    try:
        # Delete user from the 'users' table
        db["users"].delete(
            id=user.user_id,
        )

        return {"message": "User deleted successfully"}
    except Exception as e:
        print(f"Error deleting user: {e}")
        return {"error": str(e)}



'''By default SQLite will only allow one thread to communicate with it, assuming that each thread would handle an 
    independent request.

This is to prevent accidentally sharing the same connection for different things (for different requests).

But in FastAPI, using normal functions (def) more than one thread could interact with the database for the same request,
 so we need to make SQLite know that it should allow that with connect_args={"check_same_thread": False}.

Also, we will make sure each request gets its own database connection session in a dependency, so there's no need for
 that default mechanism.'''
