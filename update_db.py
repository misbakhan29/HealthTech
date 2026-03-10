import sqlite3
conn = sqlite3.connect('database/health.db')
c = conn.cursor()

# Add email column
c.execute("ALTER TABLE users ADD COLUMN email TEXT;")

conn.commit()
conn.close()
print("✅ Email column added!")
