# db_operations.py
from pydantic import BaseModel
import sqlite3


conn = sqlite3.connect('my_todo.db')
cursor = conn.cursor()


class User(BaseModel):
    username: str
    email: str
    password: str


class ToDoList(BaseModel):
    title: str


class ToDoTask(BaseModel):
    listid: int
    context: str
    completed: int











'''By default SQLite will only allow one thread to communicate with it, assuming that each thread would handle an 
    independent request.

This is to prevent accidentally sharing the same connection for different things (for different requests).

But in FastAPI, using normal functions (def) more than one thread could interact with the database for the same request,
 so we need to make SQLite know that it should allow that with connect_args={"check_same_thread": False}.

Also, we will make sure each request gets its own database connection session in a dependency, so there's no need for
 that default mechanism.'''
