from fastapi import HTTPException, status, Depends, APIRouter
from app.models import ToDoList
from app.database_utils import get_db
from fastapi.responses import JSONResponse
import sqlite3

router = APIRouter()


@router.get("/todo-lists", status_code=status.HTTP_200_OK)
def get_all_todo_lists(db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.execute(
            "SELECT todo_lists.id AS list_id, todo_lists.title AS list_title, users.id AS user_id, users.username "
            "FROM todo_lists JOIN users ON todo_lists.user_id = users.id;")
        todo_lists = cursor.fetchall()
        structured_lists = [{"list_id": todo_list[0], "title": todo_list[1], "user_id": todo_list[2]}
                            for todo_list in todo_lists]

        return JSONResponse(content={"todo_lists": structured_lists}, status_code=status.HTTP_200_OK)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Get Specific List
@router.get("/todo-lists/{list_id}", status_code=status.HTTP_200_OK)
def get_a_specific_todo_list(list_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.execute(
            "SELECT todo_lists.id AS list_id, todo_lists.title AS list_title, users.id AS user_id, users.username "
            "FROM todo_lists JOIN users ON todo_lists.user_id = users.id WHERE todo_lists.id = ?", (list_id,))
        todo_list = cursor.fetchone()

        if todo_list is not None:
            structured_list = {"list_id": todo_list[0], "title": todo_list[1], "user_id": todo_list[2],
                               "username": todo_list[3]}
            return JSONResponse(content={"todo_list": structured_list}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={"error": "List not found"}, status_code=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        error_detail = {"error": "Error encountered, check details", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Create a New List to a specific user
@router.post("/todo-lists", status_code=status.HTTP_201_CREATED)
def create_todo_list(todo_list: ToDoList, db: sqlite3.Connection = Depends(get_db)):
    try:

        db.execute("INSERT INTO todo_lists (user_id, title) VALUES ( ?, ?)", [todo_list.user_id, todo_list.title])

        list_id = db.lastrowid

        return JSONResponse(content={"list_id": f"{list_id}", "message": "List created successfully"},
                            status_code=status.HTTP_201_CREATED)
    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Update Specific Lists
@router.put("/todo-lists/{list_id}")
def update_list(list_id: int, user: ToDoList, db: sqlite3.Connection = Depends(get_db)):
    try:
        existing_list = db.execute("SELECT * FROM todo_lists WHERE id=?", (list_id,)).fetchone()

        if existing_list is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")

        db.execute("UPDATE todo_lists SET title=? WHERE id=?",
                   (user.title, list_id))

        return JSONResponse(content={"message": "List updated successfully"}, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Delete Specific List
@router.delete("/todo-lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_list_user(list_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        # Delete from todo_items
        result_todo_items = db.execute("DELETE FROM todo_items WHERE list_id = ?", [list_id])

        # Delete from todo_lists
        result_todo_lists = db.execute("DELETE FROM todo_lists WHERE id = ?", [list_id])

        if result_todo_items.rowcount == 0 and result_todo_lists.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="To Do List not found")

        return JSONResponse(content={"message": "List and all related tasks deleted"}, status_code=status.HTTP_200_OK)

    except sqlite3.Error as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
