from sqlite_utils import Database

def create_database():
    db = Database("my_todo.db")

    # Define tables and their columns here
    db["users"].create({
        "id": int,
        "username": str,
        "email": str,
        "password": str
    }, pk="id")  # Specify 'id' as the primary key

    db["todo_lists"].create({
        "id": int,
        "user_id": int,
        "title": str
    })

    db["todo_items"].create({
        "id": int,
        "list_id": int,
        "content": str,
        "completed": bool
    })

