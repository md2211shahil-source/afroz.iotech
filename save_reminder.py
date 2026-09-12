import sqlite3

connection = sqlite3.connect("reminders.db")
cursor = connection.cursor()

# Reminder details
reminder_text = "now time is to drink water"
reminder_date = "2026-09-03"
reminder_time = "19:33"
repeat_count = 3

cursor.execute("""
INSERT INTO reminders
(reminder_text, reminder_date, reminder_time, repeat_count)
VALUES (?, ?, ?, ?)
""", (
    reminder_text,
    reminder_date,
    reminder_time,
    repeat_count
))

connection.commit()
connection.close()

print("✅ Test reminder saved!")
print("📝 Task:", reminder_text)
print("📅 Date:", reminder_date)
print("⏰ Time:", reminder_time)
print("🔊 Repeat:", repeat_count, "times")