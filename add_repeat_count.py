import sqlite3

connection = sqlite3.connect("reminders.db")
cursor = connection.cursor()

cursor.execute("""
ALTER TABLE reminders
ADD COLUMN repeat_count INTEGER DEFAULT 1
""")

connection.commit()
connection.close()

print("✅ Repeat count added successfully!")