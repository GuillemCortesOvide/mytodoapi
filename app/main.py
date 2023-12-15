from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from app.db_operations import User, BaseModel, ToDo
import sqlite3
from sqlite_utils import Database


db = Database("my_todo.db")
app = FastAPI()


def get_db():
    with sqlite3.connect("my_todo.db") as connection:
        cursor = connection.cursor()
        yield cursor
        connection.commit()


@app.get("/users", status_code=status.HTTP_200_OK)
def get_users():
    try:
        conn = sqlite3.connect('my_todo.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        conn.close()

        return JSONResponse(content={"users": users}, status_code=status.HTTP_200_OK)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: User):
    try:
        conn = sqlite3.connect('my_todo.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", [user.username, user.email, user.password])
        conn.commit()
        conn.close()

        return JSONResponse(content={"message": "User inserted successfully"}, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int):
    try:
        conn = sqlite3.connect('my_todo.db')
        cursor = conn.cursor()

        # Assuming 'id' is the primary key for the 'users' table
        cursor.execute("DELETE FROM users WHERE id = ?", [id])
        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/todo-lists/{id}", status_code=status.HTTP_201_CREATED)
def create_todo_list(id: int, user: ToDo):
    try:
        with sqlite3.connect('my_todo.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO todo_lists (user_id, title) VALUES (?, ?)", [id, user.title])
            conn.commit()

        return JSONResponse(content={"message": "List inserted successfully"}, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.delete("/todo-lists/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int):
    try:
        conn = sqlite3.connect('my_todo.db')
        cursor = conn.cursor()

        # Assuming 'id' is the primary key for the 'users' table
        cursor.execute("DELETE FROM todo_lists WHERE user_id = ?", [id])
        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/todo-lists", status_code=status.HTTP_200_OK)
def get_all_todo_lists():
    try:
        conn = sqlite3.connect('my_todo.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM todo_lists")
        users = cursor.fetchall()
        conn.close()

        return JSONResponse(content={"todo_lists": users}, status_code=status.HTTP_200_OK)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/todo/{id}")
def read_user_tasks(user_id: int):
    result = read_todo(id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return result
    pass


@app.put("/todo/{id}")
def update_todo(user_id: int, todo: BaseModel):
    result = update_todo(id, todo)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return {"message": f"Todo with id {id} updated successfully"}
    pass


@app.put("/users/{id}")
def update_user(user_id: int, user: User):
    result = update_user(id, user)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": f"User with id {id} updated successfully"}
    pass


@app.delete("/todo/{id}")
def delete_todo(user_id: int):
    result = delete_todo(id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return {"message": f"Todo with id {id} deleted successfully"}
    pass


@app.get("/todo-tasks")
def read_todo_list():
    result = read_todo_list()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No todos found")
    return result
    pass
