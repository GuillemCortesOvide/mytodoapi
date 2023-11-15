# db_operations.py
from sqlite_utils import Database
from pydantic import BaseModel

# Assuming your database file is named 'your_database.db'
db = Database("my_todo.db")

class DatabaseManager:
    def __init__(self, db_file="your_database.db"):
        self.db_file = db_file
        self.db = None

    def get_db(self):
        if self.db is None:
            self.db = Database(self.db_file)
        return self.db

    def close_db(self):
        if self.db is not None:
            self.db.close()
            self.db = None

# Create a single instance of DatabaseManager
db_manager = DatabaseManager()

class User(BaseModel):
    username: str
    email: str
    password: str

def insert_user(user: User):
    try:
        db = db_manager.get_db()
        # Insert user into the 'users' table
        user_id = db["users"].insert({
            "username": user.username,
            "email": user.email,
            "password": user.password
        })["id"]

        # Insert a todo list for the user
        db["todo_lists"].insert({
            "user_id": user_id,
            "title": f"{user.username}'s Todo List"
        })

        # Commit the transaction
        db.commit()
        return {"message": "User inserted successfully"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db_manager.close_db()
    

def close_db_connection():
    db.close()