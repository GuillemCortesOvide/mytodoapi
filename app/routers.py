# routers.py
from fastapi import APIRouter, HTTPException
from sqlite_utils import Database
from pydantic import BaseModel


router = APIRouter()


class UserCreate(BaseModel):
    username: str
    email: str
    password: str




def open_db():
    db = Database("my_todo.db")
    try:
        yield db
    finally:
        db.conn.close()

















