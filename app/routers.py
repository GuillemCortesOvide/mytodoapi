# routers.py
from fastapi import APIRouter, HTTPException
from sqlite_utils import Database
from pydantic import BaseModel
from typing import Dict, Any
from starlette import status

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserId(BaseModel):
    id: int



def open_db():
    db = Database("my_todo.db")
    try:
        yield db
    finally:
        db.conn.close()


@router.post("/users/", response_model=Dict[str, Any])
def insert_user(user_data: UserCreate):
    response_data = {"message": None, "error": None}
    try:
        with open_db() as db:
            db["users"].insert({
                "username": user_data.username,
                "email": user_data.email,
                "password": user_data.password
            })
        response_data["message"] = "User created successfully"
    except Exception as e:
        response_data["error"] = str(e)

    return response_data


@router.delete("/users/{id}", response_model=Dict[str, Any])
def delete_user(id: int):
    response_data = {"message": None, "error": None}
    try:
        with open_db() as db:
            db["users"].delete({
                "id": id
            })
        response_data["message"] = "User deleted successfully"
    except Exception as e:
        response_data["error"] = str(e)

    return response_data













