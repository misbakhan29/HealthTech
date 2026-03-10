import sqlite3
import os

# ✅ Create database directory if missing
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "health.db")

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Create habits table
        c.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                habit TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Create habit_completions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS habit_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER,
                date TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY (habit_id) REFERENCES habits (id)
            )
        ''')

        # Insert default admin user
        c.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', '1234')")

        conn.commit()
        print("✅ Database and tables created successfully at:", DB_PATH)

    except Exception as e:
        print("❌ Error creating database:", e)

    finally:
        conn.close()
        print("✅ Connection closed safely.")

if __name__ == "__main__":
 init_db()