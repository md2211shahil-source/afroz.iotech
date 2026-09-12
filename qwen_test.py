import requests
import json
import sqlite3
from datetime import datetime, timedelta

from time_extraction_layer import extract_time
from validation_layer import validate_reminder


# =========================================================
# USER INPUT
# =========================================================

user_text = input("\n📝 Reminder talk/write ").strip()

if not user_text:
    print("❌ Empty input.")
    print("💾 not save in database.")
    exit()


# =========================================================
# PYTHON TIME EXTRACTION
# =========================================================


user_time = extract_time(user_text)

print("\n⏰ Python extracted time:", user_time)

if user_time is None:
    print("🛑 REMINDER REJECTED")
    print("⚠️ valid time requride.")
    print("💾 not save in database.")
    exit()


# =========================================================
# CURRENT DATE
# =========================================================

today = datetime.now()
today_date = today.strftime("%Y-%m-%d")


# =========================================================
# QWEN PROMPT
# =========================================================

prompt = f"""
You are a reminder information extraction AI.

Today's date is {today_date}.

User said:
"{user_text}"

Your job is ONLY to extract reminder information.

IMPORTANT RULES:

1. User can speak Hindi, Hinglish, or English.

2. The reminder task can be ANY reasonable task.
   Examples:
   - medicine khani hai
   - chana khana hai
   - doctor ke paas jana hai
   - walk karni hai
   - coding karni hai
   - pani peena hai
   - school jana hai

3. The word "reminder" is NOT required.

4. A sentence is a reminder request when it clearly describes
   an action/task together with a time.

5. The USER'S ORIGINAL TIME is authoritative.
   Do NOT change the user's time.

6. If Python/user time is supplied separately, do not invent
   or correct another time.

7. "aaj" means today.

8. "kal" means tomorrow.

9. "subha 8 baje" means 08:00.

10. "raat 8 baje" means 20:00.

11. Keep the actual meaning of the user's task.

12. Do NOT invent a task.

13. Do NOT invent a missing time.

14. Do NOT invent a missing date.

15. If the sentence contains a time but does not clearly
    mention today/kal, use today's date.

16. If the sentence contains "kal", use tomorrow's date.

17. Do NOT convert an invalid time into another valid time.

18. If the sentence has no time, reminder_time MUST be empty.

19. Return ONLY JSON.

Return exactly this format:

{{
    "reminder_text": "task",
    "reminder_date": "YYYY-MM-DD",
    "reminder_time": "HH:MM"
}}

Examples:

User:
"Kal subha 8 baje medicine khana hai"

Output:
{{
    "reminder_text": "medicine khana hai",
    "reminder_date": "tomorrow's date",
    "reminder_time": "08:00"
}}

User:
"Kal 8 baje checkpease khana hai"

Output:
{{
    "reminder_text": "cheakpease khana hai",
    "reminder_date": "tomorrow's date",
    "reminder_time": "08:00"
}}

User:
"Aaj 1:02 baje medicine khani hai"

Output:
{{
    "reminder_text": "medicine khani hai",
    "reminder_date": "{today_date}",
    "reminder_time": "01:02"
}}

User:
"Doctor ke paas jana hai"

Output:
{{
    "reminder_text": "doctor ke paas jana hai",
    "reminder_date": "{today_date}",
    "reminder_time": ""
}}
"""


# =========================================================
# SEND REQUEST TO QWEN
# =========================================================

print("\n🤖 send request to qwen...")

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

    response.raise_for_status()

    qwen_response = response.json()["response"].strip()

except Exception as e:

    print("❌ Qwen connection error:", e)
    print("💾 not save in data base.")
    exit()


# =========================================================
# CLEAN QWEN JSON
# =========================================================

qwen_response = qwen_response.replace("```json", "")
qwen_response = qwen_response.replace("```", "")
qwen_response = qwen_response.strip()


print("\n🤖 Qwen output:")
print(qwen_response)


# =========================================================
# JSON PARSE
# =========================================================

try:

    data = json.loads(qwen_response)

except json.JSONDecodeError:

    print("\n❌ Qwen not give valid JSON .")
    print("💾 not save in database.")
    exit()


# =========================================================
# EXTRACT QWEN DATA
# =========================================================

reminder_text = str(
    data.get("reminder_text", "")
).strip()

reminder_date = str(
    data.get("reminder_date", "")
).strip()


# =========================================================
# FINAL TIME
# =========================================================
# Qwen ka time ignore.
# User ke original sentence se Python ka time final h