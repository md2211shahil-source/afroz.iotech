import sqlite3
from datetime import datetime, timedelta

# Laptop ka current real date/time
now = datetime.now()

# 2 minutes future ka time
reminder_time = now + timedelta(minutes=2)

reminder_date = reminder_time.strftime("%Y-%m-%d")
reminder_clock = reminder_time.strftime("%H:%M")

reminder_text = "now for eating medicine"
repeat_count = 3

connection = sqlite3.connect("reminders.db")
cursor = connection.cursor()

cursor.execute("""
INSERT INTO reminders
(reminder_text, reminder_date, reminder_time, repeat_count, completed)
VALUES (?, ?, ?, ?, ?)
""", (
    reminder_text,
    reminder_date,
    reminder_clock,
    repeat_count,
    0
))

connection.commit()
connection.close()

print("✅ Test reminder successfully saved!")
print("📝 Task:", reminder_text)
print("📅 Date:", reminder_date)
print("⏰ Time:", reminder_clock)
print("🔊 Repeat:", repeat_count, "times")
print("💻 Laptop current time:", now.strftime("%Y-%m-%d %H:%M:%S"))
print("⏳ Reminder 2 minutes baad chalega.")