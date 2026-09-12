import requests
import json
import sqlite3
from datetime import datetime, timedelta

import sounddevice as sd
import numpy as np
import speech_recognition as sr

from time_extraction_layer import extract_time
from validation_layer import validate_reminder


# =========================================================
# VOICE INPUT
# =========================================================

def get_voice_input():

    print("\n🎤 say 8 secands..")
    

    duration = 8
    sample_rate = 16000

    try:

        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
            device=1
        )

        sd.wait()

    except Exception as e:

        print("❌ Microphone error:", e)
        return None

    print("✅ Recording complete!")

    audio_int16 = (audio * 32767).astype(np.int16)
    audio_bytes = audio_int16.tobytes()

    recognizer = sr.Recognizer()

    audio_data = sr.AudioData(
        audio_bytes,
        sample_rate,
        2
    )

    print("🔄 convert voice to text...")

    try:

        text = recognizer.recognize_google(audio_data)

        print("📝 You said:", text)

        return text

    except sr.UnknownValueError:

        print("❌ Voice is not undestandable.")
        return None

    except sr.RequestError as e:

        print("❌ Speech service error:", e)
        return None


# =========================================================
# DATABASE SAVE
# =========================================================

def save_reminder(
    reminder_text,
    reminder_date,
    reminder_time
):

    try:

        connection = sqlite3.connect("reminders.db")
        cursor = connection.cursor()

        cursor.execute("""
        INSERT INTO reminders
        (
            reminder_text,
            reminder_date,
            reminder_time,
            repeat_count,
            completed
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            reminder_text,
            reminder_date,
            reminder_time,
            3,
            0
        ))

        connection.commit()
        connection.close()

        return True

    except Exception as e:

        print("\n❌ Database error:", e)
        return False


# =========================================================
# QWEN EXTRACTION
# =========================================================

def extract_with_qwen(
    user_text,
    today_date
):

    prompt = f"""
You are a STRICT reminder extraction AI.

Today's date is {today_date}.

User input:
"{user_text}"

Your job is ONLY to determine whether this is a genuine reminder request
and extract the task and date.

RULES:

1. User may speak Hindi, Hinglish, or English.
2. The task can be ANY reasonable everyday task.
3. A reminder must contain a clear task/action.
4. A valid time is already checked separately by Python.
5. NEVER invent a missing task.
6. NEVER invent a missing date.
7. NEVER invent a missing time.
8. NEVER change the user's time.
9. "aaj" means today.
10. "kal" means tomorrow.
11. If no date is mentioned, use today.
12. Normal conversation is NOT a reminder.
13. Greetings are NOT reminders.
14. Questions are NOT reminders.
15. Abusive or meaningless input is NOT a reminder.
16. Keep the actual task meaning.
17. Do not return explanations.
18. Return ONLY JSON.

Examples:

Input:
"kal 8 baje medicine khani hai"

Output:
{{
    "valid": true,
    "reminder_text": "medicine khani hai",
    "reminder_date": "tomorrow"
}}



Input:
"tomorrow at 8 am I need to take my medicine"

Output:
{{
    "valid": true,
    "reminder_text": "take my medicine",
    "reminder_date": "tomorrow"
}}

Input:
"main kal doctor ke paas jaunga"

Output:
{{
    "valid": false,
    "reminder_text": "",
    "reminder_date": ""
}}

Input:
"hello how are you"

Output:
{{
    "valid": false,
    "reminder_text": "",
    "reminder_date": ""
}}

Return exactly:

{{
    "valid": true or false,
    "reminder_text": "task",
    "reminder_date": "YYYY-MM-DD or today or tomorrow"
}}
"""

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

        result = response.json()["response"].strip()

    except Exception as e:

        print("\n❌ Qwen connection error:", e)
        return None

    result = result.replace("```json", "")
    result = result.replace("```", "")
    result = result.strip()

    print("\n🤖 Qwen output:")
    print(result)

    try:

        return json.loads(result)

    except json.JSONDecodeError:

        print("\n❌ Qwen ne valid JSON nahi diya.")
        return None


# =========================================================
# MAIN APPLICATION
# =========================================================

print()
print("=" * 60)
print("        ALZHEIMER VOICE ASSISTANT")
print("        SMART REMINDER SYSTEM")
print("=" * 60)


# =========================================================
# INPUT METHOD
# =========================================================

print("\nChoose input method:")

print("1. 📝 Text Reminder")
print("2. 🎤 Voice Reminder")
print("3. ❌ Exit")

choice = input("\nEnter 1, 2 or 3: ").strip()


# =========================================================
# EXIT
# =========================================================

if choice == "3":

    print("\n👋 Alzheimer Voice Assistant closed.")
    exit()


# =========================================================
# TEXT INPUT
# =========================================================

if choice == "1":

    user_text = input(
        "\n📝 Reminder bolo/likho: "
    ).strip()


# =========================================================
# VOICE INPUT
# =========================================================

elif choice == "2":

    user_text = get_voice_input()

    if user_text is None:

        print("\n🛑 REMINDER REJECTED")
        print("💾 Database mein save NAHI hoga.")
        exit()


# =========================================================
# INVALID CHOICE
# =========================================================

else:

    print("\n❌ Invalid choice.")
    print("only select 1, 2  3 .")
    exit()


# =========================================================
# EMPTY INPUT
# =========================================================

if not user_text:

    print("\n🛑 REMINDER REJECTED")
    print("⚠️ Empty input.")
    print("💾 not save in Database.")
    exit()


print("\n📥 User input:")
print(user_text)


# =========================================================
# PYTHON TIME EXTRACTION
# =========================================================

print("\n⏰ Time Extraction Layer checking...")

user_time = extract_time(user_text)

print("⏰ Python extracted time:", user_time)


if user_time is None:

    print("\n🛑 REMINDER REJECTED")
    print("⚠️ Valid time required.")
    print("💾 not save in Database.")
    exit()


# =========================================================
# CURRENT DATE
# =========================================================

today = datetime.now()

today_date = today.strftime("%Y-%m-%d")


# =========================================================
# QWEN
# =========================================================

data = extract_with_qwen(
    user_text,
    today_date
)


if data is None:

    print("\n🛑 REMINDER REJECTED")
    print("💾 not save in Database.")
    exit()


# =========================================================
# QWEN VALIDITY
# =========================================================

qwen_valid = data.get(
    "valid",
    False
)


if qwen_valid is not True:

    print("\n🛑 REMINDER REJECTED")
    print("⚠️ this is not valid reminder.")
    print("💾 not save in Database.")
    exit()


# =========================================================
# EXTRACT TASK
# =========================================================

reminder_text = str(
    data.get(
        "reminder_text",
        ""
    )
).strip()


if not reminder_text:

    print("\n🛑 REMINDER REJECTED")
    print("⚠️ Reminder task missing .")
    print("💾 not save in Database.")
    exit()


# =========================================================
# EXTRACT DATE
# =========================================================

reminder_date = str(
    data.get(
        "reminder_date",
        ""
    )
).strip()


if reminder_date.lower() == "tomorrow":

    reminder_date = (
        today + timedelta(days=1)
    ).strftime("%Y-%m-%d")


elif reminder_date.lower() == "today":

    reminder_date = today_date


elif reminder_date.lower() == "kal":

    reminder_date = (
        today + timedelta(days=1)
    ).strftime("%Y-%m-%d")


elif reminder_date.lower() == "aaj":

    reminder_date = today_date


# =========================================================
# FINAL TIME
# =========================================================

reminder_time = user_time


# =========================================================
# VALIDATION LAYER
# =========================================================

print("\n🛡️ ReminderValidationLayer checking...")

try:

    valid, errors = validate_reminder(
        reminder_text,
        reminder_date,
        reminder_time
    )

except Exception as e:

    print("\n❌ Validation layer error:", e)
    print("💾 not save in Database.")
    exit()


# =========================================================
# VALIDATION FAILED
# =========================================================

if not valid:

    print("\n🛑 REMINDER REJECTED")
    print("💾 not save in Database.")

    for error in errors:

        print("⚠️", error)

    exit()


# =========================================================
# FINAL DISPLAY
# =========================================================

print()
print("=" * 60)
print("              ✅ REMINDER VALIDATED")
print("=" * 60)

print("📝 Task :", reminder_text)
print("📅 Date :", reminder_date)
print("⏰ Time :", reminder_time)
print("=" * 60)


# =========================================================
# SAVE
# =========================================================

print("\n💾save reminder in Database...")

saved = save_reminder(
    reminder_text,
    reminder_date,
    reminder_time
)


if not saved:

    print("\n🛑  not save Reminder .")
    exit()


# =========================================================
# SUCCESS
# =========================================================

print()
print("=" * 60)
print("       ✅ REMINDER SUCCESSFULLY SAVED")
print("=" * 60)

print("📝 Task   :", reminder_text)
print("📅 Date   :", reminder_date)
print("⏰ Time   :", reminder_time)
print("🔊 Repeat : 3 times")

print("=" * 60)
print("✅ Main application test successful!")
print("=" * 60)