from sqlite_utils import Database

def get_user_by_id(user_id):

    db = Database("my_todo.db")  # Connect to the database

    user = db["users"].get(user_id=user_id)  # Query the database for the user

    db.close()  # Close the connection

    return user


