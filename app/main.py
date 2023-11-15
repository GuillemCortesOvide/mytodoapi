from fastapi import FastAPI, HTTPException, status, Depends
from app.routers import router
from app.db_operations import insert_user, User, close_db_connection, DatabaseManager 
from app.db_operations import BaseModel
import logging

app = FastAPI()
app.include_router(router)

logging.basicConfig(level=logging.DEBUG)

def get_db_dependency():
    db_manager = DatabaseManager()
    try:
        db = db_manager.get_db()
        yield db
    finally:
        db_manager.close_db()

@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: User, db: DatabaseManager = Depends(get_db_dependency)):
    try:
        result = insert_user(db, user)
        if "error" in result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    finally:
        close_db_connection()

# Add similar modifications to other routes using the `DatabaseManager` class.



@app.post("/todo", status_code=status.HTTP_201_CREATED)
def create_todo(todo: BaseModel):  # Assuming you have a Todo Pydantic model
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