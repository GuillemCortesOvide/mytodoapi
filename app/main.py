import os
from fastapi import Request
from app.app_instance import app
from fastapi.responses import JSONResponse
from app.routers import users, todo_lists, todo_items


app.include_router(users.router)
app.include_router(todo_lists.router)
app.include_router(todo_items.router)

# Load DATABASE_URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/my_todo.db")

# Ensure directories exist if using SQLite
if DATABASE_URL.startswith("sqlite:///"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)


# This function redirects the requests in case the users adds "/" at the end of the endpoints
@app.middleware("http")
async def remove_trailing_slash(request: Request, call_next):
    if request.url.path == "/users/":
        return JSONResponse(
            status_code=301,
            content={"message": "Moved Permanently", "location": "/users"}
        )

    if request.url.path == "/todo-lists/":
        return JSONResponse(
            status_code=301,
            content={"message": "Moved Permanently", "location": "/todo-lists"}
        )

    if request.url.path == "/todo-items/":
        return JSONResponse(
            status_code=301,
            content={"message": "Moved Permanently", "location": "/todo-items"}
        )

    response = await call_next(request)
    return response
