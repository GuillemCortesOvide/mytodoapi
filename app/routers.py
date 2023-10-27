from fastapi import APIRouter
from db_operations import get_user_by_id

router = APIRouter()

@router.post("/users/")
def create_user(user_data: dict):
    pass

@router.get("/users/{user_id}")
def get_user(user_id: int):
    user = get_user_by_id(user_id)  # Call the function to fetch user from the database

    if user is not None:
        return {"user": user}
    else:
        return {"message": "User not found"}, 404

