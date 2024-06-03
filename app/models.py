from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    password: str


class ToDoList(BaseModel):
    user_id: int
    title: str


class ToDoTask(BaseModel):
    list_id: int
    context: str
    completed: int


class DeleteUser(BaseModel):
    user_id: int
