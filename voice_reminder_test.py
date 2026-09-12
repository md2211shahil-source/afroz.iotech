import sounddevice as sd
import numpy as np
import speech_recognition as sr
import requests
import json
import sqlite3

from datetime import datetime, timedelta

from time_extraction_layer import extract_time
from validation_layer import validate_reminder


# ==========================================
# VOICE INPUT
# ==========================================

print("\n🎤 8 seconds tak bolo...")
print("🎙️ Example:")
print("Tomorrow at 8 AM, I need to take my medicine.")

duration = 8
sample_rate = 16000

audio = sd.rec(
    int(duration * sample_rate),
    samplerate=sample_rate,
    channels=1,
    dtype="float32",
    device=1
)

sd.wait()

print("✅ Recording complete!")

# ==========================================
# MICROPHONE CHECK
# ==========================================

level = np.max(np.abs(audio))

print("🎚️ Microphone level:", level)

if level < 0.02:
    print("❌ Awaaz bahut low hai.")
    exit()

# ==========================================
# CONVERT AUDIO
# ==========================================

audio_int16 = (audio * 32767).astype(np.int16)
audio_bytes = audio_int16.tobytes()

recognizer = sr.Recognizer()

audio_data = sr.AudioData(
    audio_bytes,
    sample_rate,
    2
)

print("🔄 Voice ko text mein convert kar raha hoon...")

try:

    user_text = recognizer.recognize_google(
        audio_data,
        language="en-IN"
    ).strip()

except sr.UnknownValueError:

    print("❌ Voice samajh nahi aayi.")
    exit()

except sr.RequestError as e:

    print("❌ Speech service error:", e)
    exit()


print("\n📝 Voice converted text:")
print(user_text)


# ==========================================
# PYTHON TIME EXTRACTION
# ==========================================

user_time = extract_time(user_text)

print("\n⏰ Python extracted time:", user_time)

if user_time is None:

    print("🛑 REMINDER REJECTED")
    print("⚠️ User sentence mein valid time required hai.")
    print("💾 Database mein save NAHI hoga.")

    exit()


# ==========================================
# CURRENT DATE
# ==========================================

today = datetime.now()

today_date = today.strftime("%Y-%m-%d")


# ==========================================
# QWEN PROMPT
# ==========================================

prompt = f"""
You are a reminder information extraction AI.

Today's date is {today_date}.

User said:
"{user_text}"

Extract the reminder task and date.

IMPORTANT RULES:

1. User can speak English, Hindi, Hinglish, or mixed language.
2. The task can be ANY reasonable task.
3. A time is already extracted by Python.
4. Do NOT invent a task.
5. Do NOT invent a date.
6. Do NOT change the user's task.
7. "tomorrow" or "kal" means tomorrow.
8. "today" or "aaj" means today.
9. Keep the actual meaning of the user's task.
10. Return ONLY JSON.

The Python program will provide the final reminder time.

Return exactly:

{{
    "reminder_text": "task",
    "reminder_date": "YYYY-MM-DD"
}}

Example:

User:
"Tomorrow at 8 AM, I need to take my medicine."

Output:

{{
    "reminder_text": "take my medicine",
    "reminder_date": "tomorrow"
}}

User:
"Tomorrow at 6 PM I need to go to doctor."

Output:

{{
    "reminder_text": "go to doctor",
    "reminder_date": "tomorrow"
}}
"""


# ==========================================
# SEND TO QWEN
# ==========================================

print("\n🤖 Qwen ko request bhej raha hoon...")

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
    exit()


# ==========================================
# CLEAN JSON
# ==========================================

qwen_response = qwen_response.replace("```json", "")
qwen_response = qwen_response.replace("```", "")
qwen_response = qwen_response.strip()


print("\n🤖 Qwen output:")
print(qwen_response)


# ==========================================
# JSON PARSE
# ==========================================

try:

    data = json.loads(qwen_response)

except json.JSONDecodeError:

    print("\n❌ Qwen ne valid JSON nahi diya.")
    print("💾 Database mein save NAHI hoga.")
    exit()


# ==========================================
# EXTRACT DATA
# ==========================================

reminder_text = str(
    data.get("reminder_text", "")
).strip()

reminder_date = str(
    data.get("reminder_date", "")
).strip()


# ==========================================
# HANDLE TOMORROW
# ==========================================

if reminder_date.lower() in ["tomorrow", "kal"]:

    reminder_date = (
        today + timedelta(days=1)
    ).strftime("%Y-%m-%d")


# ==========================================
# USE PYTHON EXTRACTED TIME
# ==========================================

reminder_time = user_time


# ==========================================
# VALIDATION LAYER
# ==========================================

print("\n🛡️ Reminder Validation Layer checking...")


valid, errors = validate_reminder(
    reminder_text,
    reminder_date,
    reminder_time
)


if not valid:

    print("\n🛑 REMINDER REJECTED")
    print("💾 Database mein save NAHI hoga.")

    for error in errors:
        print("⚠️", error)

    exit()


# ==========================================
# VALIDATED
# ==========================================

print("\n" + "=" * 45)
print("✅ REMINDER VALIDATED")
print("=" * 45)

print("📝 Task:", reminder_text)
print("📅 Date:", reminder_date)
print("⏰ Time:", reminder_time)


# ==========================================
# SAVE TO DATABASE
# ==========================================

connection = sqlite3.connect("reminders.db")

cursor = connection.cursor()

cursor.execute(
    """
    INSERT INTO reminders
    (reminder_text, reminder_date, reminder_time, repeat_count, completed)
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        reminder_text,
        reminder_date,
        reminder_time,
        3,
        0
    )
)

connection.commit()
connection.close()


# ==========================================
# SUCCESS
# ==========================================

print("\n💾 Reminder successfully saved!")
print("📝 Task:", reminder_text)
print("📅 Date:", reminder_date)
print("⏰ Time:", reminder_time)
print("🔊 Repeat: 3 times")

print("\n✅ VOICE REMINDER SYSTEM TEST SUCCESSFUL!")