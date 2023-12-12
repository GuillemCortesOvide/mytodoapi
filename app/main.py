from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from app.db_operations import User, BaseModel, UserId
import sqlite3
from sqlite_utils import Database


db = Database("my_todo.db")
app = FastAPI()


def get_db():
    with sqlite3.connect("my_todo.db") as connection:
        cursor = connection.cursor()
        yield cursor
        connection.commit()
        results = cursor.fetchall()
    results = cursor.fetchall()


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
def delete_user(id: UserId):
    try:
        conn = sqlite3.connect('my_todo.db')
        cursor = conn.cursor()

        # Assuming 'id' is the primary key for the 'users' table
        cursor.execute("DELETE FROM users WHERE id = ?", [id.id])
        conn.commit()
        conn.close()

        return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        error_detail = {"error": "Internal Server Error", "details": str(e)}
        return JSONResponse(content=error_detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



@app.post("/todo", status_code=status.HTTP_201_CREATED)
def create_todo(todo: BaseModel):
    result = create_todo(todo)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    return {"message": "Todo created successfully"}

@app.get("/todo/{id}")
def read_todo(id: int):
    result = read_todo(id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return result

@app.put("/todo/{id}")
def update_todo(id: int, todo: BaseModel):
    result = update_todo(id, todo)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return {"message": f"Todo with id {id} updated successfully"}

@app.put("/users/{id}")
def update_user(id: int, user: User):
    result = update_user(id, user)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": f"User with id {id} updated successfully"}

@app.delete("/todo/{id}")
def delete_todo(id: int):
    result = delete_todo(id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return {"message": f"Todo with id {id} deleted successfully"}

@app.get("/todo")
def read_todo_list():
    result = read_todo_list()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No todos found")
    return result

