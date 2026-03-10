import sqlite3, os

# ✅ Correct path for your database folder
db_folder = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(db_folder, exist_ok=True)
db_path = os.path.join(db_folder, 'health.db')

conn = sqlite3.connect(db_path)
c = conn.cursor()

# ✅ Users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# ✅ Habits table
c.execute('''
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    habit TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# ✅ Habit completions table (tracks daily progress)
c.execute('''
CREATE TABLE IF NOT EXISTS habit_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    UNIQUE(habit_id, date),
    FOREIGN KEY(habit_id) REFERENCES habits(id)
)
''')

# ✅ Insert default user (admin)
c.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', ('admin', '1234'))

conn.commit()
conn.close()

print("✅ Database and tables created successfully at:",db_path)