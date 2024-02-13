from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app.db_operations import User, ToDoList, ToDoTask
import sqlite3
from sqlite_utils import Database
import hashlib, logging

DATABASE_URL = "my_todo.db"
my_db = Database(DATABASE_URL)
app = FastAPI()


def get_db():
    with sqlite3.connect(DATABASE_URL) as connection:
        cursor = connection.cursor()
        try:
            yield cursor
        finally:
            connection.commit()


def hash_password(password: str) -> str:
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(password.encode('utf-8'))
    hashed_password = hash_algorithm.hexdigest()

    return hashed_password


# Users Realm -----------------------------------------


# Get All Users
@app.get("/users", status_code=status.HTTP_200_OK)
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
@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
def get_users(user_id: int, db: sqlite3.Connection = Depends(get_db)):
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
@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: User, db: sqlite3.Connection = Depends(get_db)):
    try:

        hashed_password = hash_password(user.password)

        db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                   [user.username, user.email, hashed_password])

        return JSONResponse(content={"message": "User created successfully"}, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Update Specific User
@app.put("/users/{user_id}")
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
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
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


# To Do Lists Realm -----------------------------------------------

# Get Lists
@app.get("/todo-lists", status_code=status.HTTP_200_OK)
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
@app.get("/todo-lists/{list_id}", status_code=status.HTTP_200_OK)
def get_all_todo_lists(list_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.execute(
            "SELECT todo_lists.id AS list_id, todo_lists.title AS list_title, users.id AS user_id, users.username "
            "FROM todo_lists JOIN users ON todo_lists.user_id = users.id WHERE todo_lists.id = ?", (list_id,))
        todo_list = cursor.fetchone()
        if todo_list is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")

        structured_list = [{"list_id": todo_list[0], "title": todo_list[1], "user_id": todo_list[2]}]

        return JSONResponse(content={"todo_lists": structured_list}, status_code=status.HTTP_200_OK)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Create a New List to a specific user
@app.post("/todo-lists/{user_id}", status_code=status.HTTP_201_CREATED)
def create_todo_list(user_id: int, todo_list: ToDoList, db: sqlite3.Connection = Depends(get_db)):
    try:

        db.execute("INSERT INTO todo_lists (user_id, title) VALUES ( ?, ?)", [user_id, todo_list.title])

        return JSONResponse(content={"message": "List created successfully"}, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Update Specific Lists
@app.put("/todo-lists/{list_id}")
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
@app.delete("/todo-lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
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


# To Do Items Realm ------------------------------------------------------------


# Get All Tasks
@app.get("/todo-items", status_code=status.HTTP_200_OK)
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


# Get Tasks from a specific list
@app.get("/todo-items/{list_id}", status_code=status.HTTP_200_OK)
def get_todo_tasks(list_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db.execute(
            "SELECT todo_items.id AS todo_task_id, todo_items.list_id AS list_id, "
            "todo_lists.title AS title, "
            "todo_items.context AS task, todo_items.completed AS status "
            "FROM todo_items "
            "JOIN todo_lists ON todo_items.list_id = todo_lists.id "
            "WHERE todo_items.list_id = ?;", [list_id])

        tasks = cursor.fetchall()

        structured_tasks = [
            {
                "task_id": task[0],
                "list_id": task[1],
                "title": task[2],
                "context": task[3],
                "completed": task[4],
            }
            for task in tasks
        ]

        return JSONResponse(content={"specific_task": structured_tasks}, status_code=status.HTTP_200_OK)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Create a new task for specific list and user
@app.post("/todo-items/{list_id}/{user_id}", status_code=status.HTTP_201_CREATED)
def create_todo_task(list_id: int, user: ToDoTask, db: sqlite3.Connection = Depends(get_db)):
    try:
        existing_list = db.execute("SELECT id FROM todo_lists WHERE id=?", (list_id,)).fetchone()
        if not existing_list:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")

        db.execute("INSERT INTO todo_items (list_id, context, completed) VALUES (?, ?, ?)",
                   [list_id, user.context, user.completed])

        return JSONResponse(content={"message": "Task inserted successfully"}, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Update specific task from a list
@app.put("/todo-items/{list_id}")
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
@app.delete("/todo-items/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo_item(task_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        # Assuming 'id' is the primary key for the 'todo_items' table

        result = db.execute("DELETE FROM todo_items WHERE id = ?", [task_id])

        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

        return JSONResponse(content={"message": "Task deleted successfully"}, status_code=status.HTTP_200_OK)

    except sqlite3.Error as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
