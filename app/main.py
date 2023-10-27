from fastapi import FastAPI, status
from routers import router

app = FastAPI()
app.include_router(router)

@app.get("/")
def read_root():
    return "My To Do List"

# create a todo item method "POST" path "/todo"

@app.post("/todo", status_code=status.HTTP_201_CREATED)
def create_todo():
    return "create a todo item"

# read a todo list item method "GET" path "/todo/{id}"

@app.get("/todo/{id}")
def read_todo(id:int):
    return "read a todo item with id {id}"


# update a todo item method "PUT" path "/todo/{id}"

@app.put("/todo/{id}")
def update_todo(id:int):
    return "update todo item with id {id}"



# delete a todo item "DELETE" path "/todo/{id}"

@app.delete("/todo/{id}")
def delete_todo(id:int):
    return "delete todo item with id {id}"

# read all todo items "GET" path "/todo"

@app.get("/todo")
def read_todo_list():
    return "read todo list"