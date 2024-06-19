from fastapi import HTTPException, status, Depends, APIRouter
from app.models import User, DeleteUser
from app.database_utils import get_db, hash_password
from fastapi.responses import JSONResponse
import sqlite3

router = APIRouter()


@router.get("/users", status_code=status.HTTP_200_OK)
def get_users(db: sqlite3.Connection = Depends(get_db)):

    try:
        cursor = db
        cursor.execute("SELECT id, username, email FROM users")
        users = cursor.fetchall()
        structured_users = [{"user_id": user[0], "username": user[1], "mail": user[2]} for user in users]

        return JSONResponse(content={"users": structured_users}, status_code=status.HTTP_200_OK)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Get Specific User
@router.get("/users/{user_id}", status_code=status.HTTP_200_OK)
def get_specific_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db
        cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if user:
            structured_user = {"user_id": user[0], "username": user[1], "mail": user[2]}
            return JSONResponse(content={"user": structured_user}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={"error": "User not found"}, status_code=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Create New User
@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: User, db: sqlite3.Connection = Depends(get_db)):
    try:

        hashed_password = hash_password(user.password)

        db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                   [user.username, user.email, hashed_password])

        user_id = db.lastrowid

        return JSONResponse(content={"user_id": user_id, "message": "User created successfully"},
                            status_code=status.HTTP_201_CREATED)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Update Specific User
@router.put("/users/{user_id}")
def update_user(user_id: int, user: User, db: sqlite3.Connection = Depends(get_db)):
    try:
        existing_user = db.execute("SELECT * FROM USERS WHERE id=?", (user_id,)).fetchone()
        if existing_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        hashed_password = hash_password(user.password) if user.password else existing_user[3]

        db.execute("UPDATE users SET username=?, email=?, password=? WHERE id=?",
                   (user.username, user.email, hashed_password, user_id))
        return JSONResponse(content={"message": "User updated successfully"}, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Delete Specific User
@router.delete("/users", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user: DeleteUser, db: sqlite3.Connection = Depends(get_db)):
    try:
        user_id = user.user_id
        # Delete tasks associated with the user
        db.execute("DELETE FROM todo_items WHERE list_id IN (SELECT id FROM todo_lists WHERE user_id = ?)", [user_id])

        # Delete lists associated with the user
        db.execute("DELETE FROM todo_lists WHERE user_id = ?", [user_id])

        # Delete the user
        result = db.execute("DELETE FROM users WHERE id = ?", [user_id])

        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return JSONResponse(content={"message": "User and all related data deleted"}, status_code=status.HTTP_200_OK)

    except sqlite3.Error as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
