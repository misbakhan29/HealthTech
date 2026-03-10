import sqlite3
import os

# find your existing database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'health.db')  # change path if needed

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS habit_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    UNIQUE(habit_id, date)
)
''')

conn.commit()
conn.close()
print("✅ Daily tracking table created successfully!")