import sqlite3, os

# Path to your database
db_path = os.path.join(os.path.dirname(__file__), 'database', 'health.db')

# Connect to DB
conn = sqlite3.connect(db_path)

# Create the table if it doesn’t exist
conn.execute("""
CREATE TABLE IF NOT EXISTS habit_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER,
    date TEXT,
    status TEXT DEFAULT 'Pending'
)
""")

conn.commit()
conn.close()

print("✅ Table 'habit_completions' created successfully!")