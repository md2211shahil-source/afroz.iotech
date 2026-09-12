import sqlite3

# Database create/connect
connection = sqlite3.connect("reminders.db")

cursor = connection.cursor()

# Reminders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reminder_text TEXT NOT NULL,
    reminder_date TEXT NOT NULL,
    reminder_time TEXT NOT NULL,
    completed INTEGER DEFAULT 0
)
""")

connection.commit()
connection.close()

print("✅ Database ready!")
print("💾 reminders.db created successfully.")