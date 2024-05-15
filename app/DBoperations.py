from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    password: str


class ToDoList(BaseModel):
    title: str


class ToDoTask(BaseModel):
    context: str
    completed: int


