from fastapi import Request, FastAPI
from app.app_instance import app
from fastapi.responses import JSONResponse
from sqlite_utils import Database
from app.config import DATABASE_URL
import os
from app.routers import users, todo_lists, todo_items


my_db = Database(DATABASE_URL)

app.include_router(users.router)
app.include_router(todo_lists.router)
app.include_router(todo_items.router)

# create the database directory if it does not exist

os.makedirs(os.path.dirname(DATABASE_URL), exist_ok=True)


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
