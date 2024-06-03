from fastapi import HTTPException, status, Depends, APIRouter
from app.models import ToDoTask
from app.database_utils import get_db
from fastapi.responses import JSONResponse
import sqlite3

router = APIRouter()


@router.get("/todo-items", status_code=status.HTTP_200_OK)
def get_todo_tasks(db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.execute(
            "SELECT todo_items.id AS todo_task_id, todo_items.list_id AS list_id, "
            "todo_items.context AS task, todo_items.completed AS status, "
            "todo_lists.title AS title "
            "FROM todo_items "
            "LEFT JOIN todo_lists ON todo_items.list_id = todo_lists.id;")

        todo_items = cursor.fetchall()

        structured_tasks = [
            {
                "task_id": task[0],
                "list_id": task[1],
                "list_title": task[4],
                "context": task[2],
                "completed": task[3],
            }
            for task in todo_items
        ]

        return JSONResponse(content={"todo_tasks": structured_tasks}, status_code=status.HTTP_200_OK)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Get specific task by task_id
@router.get("/todo-items/{task_id}", status_code=status.HTTP_200_OK)
def get_specific_task(task_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.execute(
            "SELECT todo_items.id AS task_id, todo_items.list_id, todo_items.context AS title, "
            "todo_items.completed AS completed "
            "FROM todo_items "
            "WHERE todo_items.id = ?;", (task_id,))
        todo_items = cursor.fetchone()
        if todo_items is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        structured_task = {
            "task_id": todo_items[0],
            "list_id": todo_items[1],
            "task": todo_items[2],
            "completed": todo_items[3]
        }

        return JSONResponse(content={"specific_task": structured_task}, status_code=status.HTTP_200_OK)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Create a new task for specific list and user
@router.post("/todo-items/{list_id}/{user_id}", status_code=status.HTTP_201_CREATED)
def create_todo_task(list_id: int, user: ToDoTask, db: sqlite3.Connection = Depends(get_db)):
    try:
        existing_list = db.execute("SELECT id FROM todo_lists WHERE id=?", (list_id,)).fetchone()
        if not existing_list:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")

        db.execute("INSERT INTO todo_items (list_id, context, completed) VALUES (?, ?, ?)",
                   [list_id, user.context, user.completed])

        return JSONResponse(content={"message": "Task inserted successfully"},
                            status_code=status.HTTP_201_CREATED)
    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Update specific task from a list
@router.put("/todo-items/{list_id}")
def update_user(list_id: int, user: ToDoTask, db: sqlite3.Connection = Depends(get_db)):
    try:

        existing_user = db.execute("SELECT * FROM todo_items WHERE list_id=?", (list_id,)).fetchone()

        if existing_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        db.execute("UPDATE todo_items SET context=?, completed=? WHERE list_id=?",
                   (user.context, user.completed, list_id))

        return JSONResponse(content={"message": "Task updated successfully"}, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Delete task from a specific list
@router.delete("/todo-items/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo_item(task_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:

        result = db.execute("DELETE FROM todo_items WHERE id = ?", [task_id])

        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

        return JSONResponse(content={"message": "Task deleted successfully"}, status_code=status.HTTP_200_OK)

    except sqlite3.Error as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
