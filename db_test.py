import sqlite3

conn = sqlite3.connect('my_todo.db')

cursor = conn.cursor()

cursor.execute("INSERT INTO users VALUES ( '6', 'Guillem', 'javier@test.com', 'mypassword')")

cursor.execute("SELECT * FROM users")

results = cursor.fetchall()
conn.commit()

print(results)