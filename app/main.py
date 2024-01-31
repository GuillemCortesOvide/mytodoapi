from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app.db_operations import User, ToDoList, ToDoTask
import sqlite3
from sqlite_utils import Database
import hashlib

DATABASE_URL = "my_test_todo.db"
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


@app.get("/users", status_code=status.HTTP_200_OK)
def get_users(db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db
        cursor.execute("SELECT id, username, email FROM users")
        users = cursor.fetchall()
        return JSONResponse(content={"users": users}, status_code=status.HTTP_200_OK)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: User, db: sqlite3.Connection = Depends(get_db)):
    try:

        hashed_password = hash_password(user.password)

        db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                   [user.username, user.email, hashed_password])

        return JSONResponse(content={"message": "User inserted successfully"}, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        db.execute("DELETE FROM users WHERE id = ?", [id])
        return None

    except sqlite3.Error as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.put("/users/{id}")
def update_user(id: int, user: User, db: sqlite3.Connection = Depends(get_db)):
    try:
        existing_user = db.execute("SELECT * FROM USERS WHERE id=?", (id,)).fetchone()
        if existing_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        hashed_password = hash_password(user.password) if user.password else existing_user[3]

        db.execute("UPDATE users SET username=?, email=?, password=? WHERE id=?",
                   (user.username, user.email, hashed_password, id))
        return JSONResponse(content={"message": "User inserted successfully"}, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/todo-lists/{user_id}", status_code=status.HTTP_201_CREATED)
def create_todo_list(user_id: int, todo_list: ToDoList, db: sqlite3.Connection = Depends(get_db)):
    try:

        db.execute("INSERT INTO todo_lists (user_id, title) VALUES ( ?, ?)", [user_id, todo_list.title])

        return JSONResponse(content={"message": "List inserted successfully"}, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.delete("/todo-lists/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_list_user(id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        # Assuming 'id' is the primary key for the 'users' table
        db.execute("DELETE FROM todo_lists WHERE id = ?", [id])

    except sqlite3.Error as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/todo-lists", status_code=status.HTTP_200_OK)
def get_all_todo_lists(db: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = db
        db.execute(
            "SELECT todo_lists.id AS list_id, todo_lists.title AS list_title, users.id AS user_id, users.username FROM todo_lists JOIN users ON todo_lists.user_id = users.id;")
        users = cursor.fetchall()
        return JSONResponse(content={"todo_lists": users}, status_code=status.HTTP_200_OK)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.put("/todo-lists/{id}")
def update_list(id: int, user: ToDoList, db: sqlite3.Connection = Depends(get_db)):
    try:
        existing_list = db.execute("SELECT * FROM todo_lists WHERE id=?", (id,)).fetchone()

        if existing_list is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")

        db.execute("UPDATE todo_lists SET title=? WHERE id=?",
                   (user.title, id))

        return JSONResponse(content={"message": "List updated successfully"}, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/todo-items/{list_id}/{id}", status_code=status.HTTP_201_CREATED)
def create_todo_task(list_id: int, user: ToDoTask):
    try:
        with sqlite3.connect('my_todo.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO todo_items (list_id, context, completed) VALUES (?, ?, ?)",
                           [list_id, user.context, user.completed])
            conn.commit()

        return JSONResponse(content={"message": "Task inserted successfully"}, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/todo-items")
def get_todo_tasks():
    try:
        conn = sqlite3.connect('my_todo.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT todo_items.id AS todo_task_id, todo_items.list_id AS user_list, todo_items.context AS task, todo_items.completed AS status, users.id AS user_id, users.username FROM todo_items JOIN users ON todo_items.id = users.id;")
        users = cursor.fetchall()
        conn.close()

        return JSONResponse(content={"users": users}, status_code=status.HTTP_200_OK)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
    return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.delete("/todo-items/{id}")
def delete_todo_item(id: int):
    try:
        conn = sqlite3.connect('my_todo.db')
        cursor = conn.cursor()
        # Assuming 'id' is the primary key for the 'todo_items' table
        cursor.execute("DELETE FROM todo_items WHERE id = ?", [id])
        conn.commit()
        conn.close()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

        return {"message": f"Todo with id {id} deleted successfully"}

    except sqlite3.Error as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.put("/todo-items/{list_id}")
def update_user(list_id: int, user: ToDoTask):
    try:
        conn = sqlite3.connect('my_todo.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM todo_items WHERE list_id=?", (list_id,))
        existing_user = cursor.fetchone()
        if existing_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        cursor.execute("UPDATE todo_items SET context=?, completed=? WHERE list_id=?",
                       (user.context, user.completed, list_id))
        conn.commit()
        conn.close()

        return JSONResponse(content={"message": "Task updated successfully"}, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
