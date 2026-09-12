import sqlite3
import requests
import json
import re
from datetime import datetime


# ---------------------------------------
# 1. User se reminder lena
# ---------------------------------------

user_text = input("📝 Apna reminder likho: ")

print("\n🧠 Qwen reminder details samajh raha hai...")


# ---------------------------------------
# 2. Today's date
# ---------------------------------------

today = datetime.now().strftime("%Y-%m-%d")


# ---------------------------------------
# 3. Qwen prompt
# ---------------------------------------

prompt = f"""
You are a STRICT reminder request classifier.

Today's date is {today}.

USER INPUT:
{user_text}

Your job is to decide whether the user wants to CREATE A REMINDER.

A valid reminder MUST contain:
1. A clear action/task
2. A clear future date or understandable date expression
3. A valid time

IMPORTANT RULES:

- General conversation is NOT a reminder.
- Greetings are NOT reminders.
- Questions are NOT reminders.
- Abuse or random text is NOT a reminder.
- Coding requests are NOT reminders unless the user clearly asks to create a reminder for coding.
- NEVER invent missing information.
- NEVER change an invalid time into a valid time.
- For example, 35:00 is INVALID.
- If the time is missing, valid MUST be false.
- If the task is missing, valid MUST be false.
- If the date is missing, valid MUST be false.
- If any required information is missing or invalid, valid MUST be false.
- Only create_reminder when all required information is valid.

Return ONLY JSON.

Use exactly this format:

{{
  "intent": "create_reminder" or "general_conversation",
  "valid": true or false,
  "reminder_text": "",
  "reminder_date": "YYYY-MM-DD",
  "reminder_time": "HH:MM"
}}
"""


# ---------------------------------------
# 4. Qwen ko request
# ---------------------------------------

try:

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

except Exception as e:

    print("\n❌ Ollama se connection nahi ho saka.")
    print("Error:", e)
    exit()


if response.status_code != 200:

    print("\n❌ Qwen error:", response.status_code)
    exit()


# ---------------------------------------
# 5. Qwen output
# ---------------------------------------

raw_output = response.json()["response"]

print("\n🤖 Qwen output:")
print(raw_output)


# ---------------------------------------
# 6. JSON extract karna
# ---------------------------------------

try:

    json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)

    if not json_match:
        raise ValueError("JSON nahi mila.")

    data = json.loads(json_match.group())

except Exception as e:

    print("\n❌ Qwen ne valid JSON nahi diya.")
    print("Error:", e)
    exit()


# ---------------------------------------
# 7. Required fields
# ---------------------------------------

intent = data.get("intent", "")
valid = data.get("valid", False)

reminder_text = data.get("reminder_text", "")
reminder_date = data.get("reminder_date", "")
reminder_time = data.get("reminder_time", "")


# ---------------------------------------
# 8. Python Safety Validation
# ---------------------------------------

errors = []


# Task check
if not reminder_text.strip():
    errors.append("Reminder task missing.")


# Date check
try:

    datetime.strptime(reminder_date, "%Y-%m-%d")

except Exception:

    errors.append("Invalid date.")


# Time check
try:

    datetime.strptime(reminder_time, "%H:%M")

except Exception:

    errors.append("Invalid time.")


# Intent / AI validation
if intent != "create_reminder":
    errors.append("this is not reminder requests .")


if valid is not True:
    errors.append("AIsays invalid request.")


# ---------------------------------------
# 9. Reject invalid reminder
# ---------------------------------------

if errors:

    print("\n🛑 REMINDER REJECTED")
    print("this is not save in data base.")

    for error in errors:
        print("⚠️", error)

    exit()


# ---------------------------------------
# 10. Save reminder
# ---------------------------------------

connection = sqlite3.connect("reminders.db")

cursor = connection.cursor()


# Repeat count default = 3
repeat_count = 3


cursor.execute(
    """
    INSERT INTO reminders
    (reminder_text, reminder_date, reminder_time, repeat_count)
    VALUES (?, ?, ?, ?)
    """,
    (
        reminder_text,
        reminder_date,
        reminder_time,
        repeat_count
    )
)


connection.commit()
connection.close()


# ---------------------------------------
# 11. Success
# ---------------------------------------

print("\n✅ REMINDER VALIDATED")
print("🔐 Python safety checks pass ho gaye.")

print("\n💾 Reminder successfully saved!")
print("📝 Task:", reminder_text)
print("📅 Date:", reminder_date)
print("⏰ Time:", reminder_time)
print("🔊 Repeat:", repeat_count, "times")