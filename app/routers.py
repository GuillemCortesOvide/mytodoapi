# routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlite_utils import Database
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@router.post("/users/", response_model=dict)
def insert_user(user_data: UserCreate):
    try:
        with Database("my_todo.db") as db:
            db["users"].insert({
                "username": user_data.username,
                "email": user_data.email,
                "password": user_data.password
            })
        return {"message": "User created successfully"}
    except Exception as e:
        return {"error": str(e)}, 500  # Return an error message and status code 500
