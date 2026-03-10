import sqlite3

# Connect to database
conn = sqlite3.connect('health.db')
cursor = conn.cursor()

# Insert a test user
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))

conn.commit()
conn.close()

print("✅ Test user added successfully! (username: admin, password: 1234)")