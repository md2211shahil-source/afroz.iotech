from flask import Flask, render_template, session, request, jsonify, redirect
import sqlite3
import requests
import json
from datetime import datetime, timedelta

import sounddevice as sd
import numpy as np
import speech_recognition as sr

from time_extraction_layer import extract_time
from validation_layer import validate_reminder


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = "alzheimer_voice_assistant_secret_key"

DATABASE = "reminders.db"


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def save_reminder(reminder_text, reminder_date, reminder_time):

    conn = get_db()

    conn.execute(
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

    conn.commit()
    conn.close()


# =========================================================
# QWEN AI EXTRACTION
# =========================================================

def extract_with_qwen(user_text, today_date):

    prompt = f"""
You extract ONE reminder from the user's sentence.

Today is: {today_date}

User sentence:
{user_text}

RULES:

1. Accept the request if it contains ONE clear action/task.
2. The user must provide a time.
3. Python already checks the user's time separately.
4. "at 8" is a valid time and means 08:00.
5. "at 8 AM" means 08:00.
6. "at 8 PM" means 20:00.
7. Do NOT invent a time.
8. Do NOT change the user's time.
9. Do NOT invent a task.
10. Convert the task into short, professional English.
11. Hindi, Hinglish and English input are allowed.
12. "aaj" / "today" means today.
13. "kal" / "tomorrow" means tomorrow.
14. If no date is mentioned, use today.
15. Only ONE task is allowed.
16. Two different tasks = invalid.
17. Greeting or normal conversation = invalid.
18. Question without a reminder task = invalid.
19. Missing task = invalid.
20. Missing time = invalid.
21. Invalid time = invalid.

IMPORTANT VALID EXAMPLES:

User: Tomorrow at 8 eat chickpeas
JSON:
{{
    "valid": true,
    "reminder_text": "Eat chickpeas",
    "reminder_date": "tomorrow"
}}

User: Aaj 9 baje dawa khana hai
JSON:
{{
    "valid": true,
    "reminder_text": "Take medicine",
    "reminder_date": "today"
}}

User: Kal 7 baje walk karna hai
JSON:
{{
    "valid": true,
    "reminder_text": "Go for a walk",
    "reminder_date": "tomorrow"
}}

IMPORTANT INVALID EXAMPLES:

User: Hello how are you
JSON:
{{
    "valid": false,
    "reminder_text": "",
    "reminder_date": ""
}}

User: Tomorrow eat chickpeas
JSON:
{{
    "valid": false,
    "reminder_text": "",
    "reminder_date": ""
}}

User: Tomorrow at 8
JSON:
{{
    "valid": false,
    "reminder_text": "",
    "reminder_date": ""
}}

User: Tomorrow at 8 eat chickpeas and go to hospital
JSON:
{{
    "valid": false,
    "reminder_text": "",
    "reminder_date": ""
}}

Return ONLY valid JSON.

Required format:
{{
    "valid": true or false,
    "reminder_text": "short English task",
    "reminder_date": "today or tomorrow"
}}
"""

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",

            json={
                "model": "qwen2.5:3b",
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "keep_alive": "10m",
                "temperature": 0,
                "num_predict": 80
            },

            timeout=180
        )

        if response.status_code != 200:

            print("Qwen HTTP Error:", response.status_code)
            print(response.text)

            return None

        data = response.json()

        qwen_response = data.get("response", "")

        print("Qwen raw response:")
        print(qwen_response)

        try:

            result = json.loads(qwen_response)

        except json.JSONDecodeError:

            print("Qwen returned invalid JSON.")

            return None

        if not isinstance(result, dict):

            print("Qwen result is not an object.")

            return None

        return result

    except requests.exceptions.Timeout:

        print("Qwen request timed out.")

        return None

    except requests.exceptions.ConnectionError:

        print("Cannot connect to Ollama.")

        return None

    except Exception as e:

        print("Qwen Error:", e)

        return None


# =========================================================
# LOGIN
# =========================================================

@app.route("/")
def login():

    # Agar user already logged in hai
    # to direct dashboard open karo.

    if session.get("logged_in"):

        return redirect("/dashboard")

    return render_template("login.html")


# =========================================================
# DO LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def do_login():

    # Login page mein agar email field hai
    # to email read karega.

    email = request.form.get("email", "").strip()

    # Agar username field hai
    # to username bhi read karega.

    username = request.form.get("username", "").strip()

    # Dono mein se jo available ho use karo.

    login_user = email or username

    print("\n==============================")
    print("LOGIN REQUEST")
    print("==============================")

    print("Email:", email)
    print("Username:", username)

    if not login_user:

        print("LOGIN FAILED: EMPTY USER")

        return render_template(
            "login.html",
            error="Please enter your email address."
        )

    # Session clear karke fresh login session create karo.

    session.clear()

    session["username"] = login_user
    session["logged_in"] = True

    session.modified = True

    print("LOGIN SUCCESS")
    print("Logged in user:", login_user)
    print("Session:", dict(session))

    # IMPORTANT:
    # Dashboard ko directly render nahi karna.
    # Redirect karna hai taaki /dashboard session check kar sake.

    return redirect("/dashboard")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    print("\n==============================")
    print("DASHBOARD REQUEST")
    print("==============================")

    print("Current session:", dict(session))

    # Login nahi hai
    if not session.get("logged_in"):

        print("NO LOGIN SESSION")
        print("REDIRECTING TO LOGIN")

        return redirect("/")

    print("LOGIN SESSION FOUND")
    print("Opening dashboard...")

    return render_template(
        "dashboard.html",
        username=session.get("username", "User")
    )


# =========================================================
# GET REMINDERS
# =========================================================

@app.route("/api/reminders", methods=["GET"])
def get_reminders():

    conn = get_db()

    rows = conn.execute(
        """
        SELECT id,
               reminder_text,
               reminder_date,
               reminder_time,
               repeat_count,
               completed
        FROM reminders
        ORDER BY reminder_date ASC, reminder_time ASC
        """
    ).fetchall()

    conn.close()

    reminders = []

    for row in rows:

        reminders.append({

            "id": row["id"],

            "reminder_text":
                row["reminder_text"],

            "reminder_date":
                row["reminder_date"],

            "reminder_time":
                row["reminder_time"],

            "repeat_count":
                row["repeat_count"],

            "completed":
                row["completed"]

        })

    return jsonify({

        "success": True,

        "reminders": reminders

    })


# =========================================================
# ADD TEXT REMINDER
# =========================================================

@app.route("/api/add-reminder", methods=["POST"])
def add_reminder():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No data received."
            }), 400

        user_text = data.get(
            "user_text",
            ""
        ).strip()

        print("\n==============================")
        print("NEW TEXT REMINDER")
        print("==============================")

        print("User input:", user_text)

        if not user_text:

            return jsonify({
                "success": False,
                "message": "Please enter a reminder."
            }), 400

        # -------------------------------------------------
        # STEP 1: PYTHON TIME EXTRACTION
        # -------------------------------------------------

        user_time = extract_time(user_text)

        print(
            "Python extracted time:",
            user_time
        )

        if user_time is None:

            return jsonify({

                "success": False,

                "message":
                    "A valid time is required. "
                    "Example: 8 AM, 20:00 or at 8."

            }), 400

        # -------------------------------------------------
        # STEP 2: TODAY DATE
        # -------------------------------------------------

        today_date = datetime.now().strftime(
            "%Y-%m-%d"
        )

        # -------------------------------------------------
        # STEP 3: QWEN EXTRACTION
        # -------------------------------------------------

        result = extract_with_qwen(
            user_text,
            today_date
        )

        print(
            "Qwen parsed result:",
            result
        )

        if not result:

            return jsonify({

                "success": False,

                "message":
                    "AI could not understand the reminder."

            }), 400

        # -------------------------------------------------
        # STEP 4: QWEN VALID FLAG
        # -------------------------------------------------

        if result.get("valid") is not True:

            return jsonify({

                "success": False,

                "message":
                    "This is not a valid single reminder."

            }), 400

        # -------------------------------------------------
        # STEP 5: TASK
        # -------------------------------------------------

        reminder_text = str(
            result.get(
                "reminder_text",
                ""
            )
        ).strip()

        if not reminder_text:

            return jsonify({

                "success": False,

                "message":
                    "Reminder task is missing."

            }), 400

        # -------------------------------------------------
        # STEP 6: DATE
        # -------------------------------------------------

        reminder_date = str(
            result.get(
                "reminder_date",
                ""
            )
        ).strip().lower()

        if reminder_date in [
            "today",
            "aaj"
        ]:

            reminder_date = today_date

        elif reminder_date in [
            "tomorrow",
            "kal"
        ]:

            tomorrow = (
                datetime.now()
                + timedelta(days=1)
            )

            reminder_date = tomorrow.strftime(
                "%Y-%m-%d"
            )

        else:

            return jsonify({

                "success": False,

                "message":
                    "Invalid reminder date."

            }), 400

        # -------------------------------------------------
        # STEP 7: TIME FROM PYTHON
        # -------------------------------------------------

        reminder_time = user_time

        print(
            "Final task:",
            reminder_text
        )

        print(
            "Final date:",
            reminder_date
        )

        print(
            "Final time:",
            reminder_time
        )

        # -------------------------------------------------
        # STEP 8: FINAL VALIDATION
        # -------------------------------------------------

        is_valid, errors = validate_reminder(

            reminder_text,

            reminder_date,

            reminder_time,

            user_text

        )

        print(
            "Validation:",
            is_valid
        )

        print(
            "Errors:",
            errors
        )

        if not is_valid:

            return jsonify({

                "success": False,

                "message":
                    "Reminder rejected.",

                "errors":
                    errors

            }), 400

        # -------------------------------------------------
        # STEP 9: SAVE
        # -------------------------------------------------

        save_reminder(

            reminder_text,

            reminder_date,

            reminder_time

        )

        print(
            "REMINDER SAVED SUCCESSFULLY"
        )

        return jsonify({

            "success": True,

            "message":
                "Reminder added successfully.",

            "reminder": {

                "reminder_text":
                    reminder_text,

                "reminder_date":
                    reminder_date,

                "reminder_time":
                    reminder_time

            }

        })

    except Exception as e:

        print(
            "ADD REMINDER ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                "Server error while adding reminder."

        }), 500


# =========================================================
# DELETE REMINDER
# =========================================================

@app.route(
    "/api/delete-reminder/<int:reminder_id>",
    methods=["DELETE"]
)
def delete_reminder(reminder_id):

    try:

        conn = get_db()

        cursor = conn.execute(

            "DELETE FROM reminders WHERE id = ?",

            (reminder_id,)

        )

        conn.commit()

        conn.close()

        if cursor.rowcount == 0:

            return jsonify({

                "success": False,

                "message":
                    "Reminder not found."

            }), 404

        return jsonify({

            "success": True,

            "message":
                "Reminder deleted successfully."

        })

    except Exception as e:

        print(
            "DELETE ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                "Could not delete reminder."

        }), 500


# =========================================================
# MICROPHONE
# =========================================================

def get_voice_input():

    SAMPLE_RATE = 16000

    RECORD_SECONDS = 8

    DEVICE_INDEX = 1

    print("\nListening...")

    try:

        audio = sd.rec(

            int(
                RECORD_SECONDS
                * SAMPLE_RATE
            ),

            samplerate=SAMPLE_RATE,

            channels=1,

            dtype="float32",

            device=DEVICE_INDEX

        )

        sd.wait()

        print(
            "Recording finished."
        )

        audio = np.squeeze(audio)

        audio_int16 = (

            audio * 32767

        ).astype(np.int16)

        audio_data = sr.AudioData(

            audio_int16.tobytes(),

            SAMPLE_RATE,

            2

        )

        recognizer = sr.Recognizer()

        print(
            "Converting speech to text..."
        )

        text = recognizer.recognize_google(

            audio_data

        )

        print(
            "Recognized text:",
            text
        )

        return text

    except sr.UnknownValueError:

        print(
            "Could not understand speech."
        )

        return None

    except sr.RequestError as e:

        print(
            "Speech recognition error:",
            e
        )

        return None

    except Exception as e:

        print(
            "Microphone error:",
            e
        )

        return None


# =========================================================
# ADD VOICE REMINDER
# =========================================================

@app.route(
    "/api/voice-reminder",
    methods=["POST"]
)
def voice_reminder():

    try:

        print("\n==============================")
        print("VOICE REMINDER")
        print("==============================")

        user_text = get_voice_input()

        if not user_text:

            return jsonify({

                "success": False,

                "message":
                    "I could not understand your voice."

            }), 400

        print(
            "Voice input:",
            user_text
        )

        # -------------------------------------------------
        # STEP 1: PYTHON TIME EXTRACTION
        # -------------------------------------------------

        user_time = extract_time(
            user_text
        )

        print(
            "Python extracted time:",
            user_time
        )

        if user_time is None:

            return jsonify({

                "success": False,

                "message":
                    "A valid time is required."

            }), 400

        # -------------------------------------------------
        # STEP 2: TODAY
        # -------------------------------------------------

        today_date = datetime.now().strftime(
            "%Y-%m-%d"
        )

        # -------------------------------------------------
        # STEP 3: QWEN
        # -------------------------------------------------

        result = extract_with_qwen(

            user_text,

            today_date

        )

        print(
            "Qwen parsed result:",
            result
        )

        if not result:

            return jsonify({

                "success": False,

                "message":
                    "AI could not understand the reminder."

            }), 400

        # -------------------------------------------------
        # STEP 4: VALID
        # -------------------------------------------------

        if result.get("valid") is not True:

            return jsonify({

                "success": False,

                "message":
                    "This is not a valid single reminder."

            }), 400

        # -------------------------------------------------
        # STEP 5: TASK
        # -------------------------------------------------

        reminder_text = str(

            result.get(
                "reminder_text",
                ""
            )

        ).strip()

        if not reminder_text:

            return jsonify({

                "success": False,

                "message":
                    "Reminder task is missing."

            }), 400

        # -------------------------------------------------
        # STEP 6: DATE
        # -------------------------------------------------

        reminder_date = str(

            result.get(
                "reminder_date",
                ""
            )

        ).strip().lower()

        if reminder_date in [
            "today",
            "aaj"
        ]:

            reminder_date = today_date

        elif reminder_date in [
            "tomorrow",
            "kal"
        ]:

            tomorrow = (

                datetime.now()
                + timedelta(days=1)

            )

            reminder_date = tomorrow.strftime(
                "%Y-%m-%d"
            )

        else:

            return jsonify({

                "success": False,

                "message":
                    "Invalid reminder date."

            }), 400

        # -------------------------------------------------
        # STEP 7: TIME FROM PYTHON
        # -------------------------------------------------

        reminder_time = user_time

        # -------------------------------------------------
        # STEP 8: FINAL VALIDATION
        # -------------------------------------------------

        is_valid, errors = validate_reminder(

            reminder_text,

            reminder_date,

            reminder_time,

            user_text

        )

        print(
            "Validation:",
            is_valid
        )

        print(
            "Errors:",
            errors
        )

        if not is_valid:

            return jsonify({

                "success": False,

                "message":
                    "Reminder rejected.",

                "errors":
                    errors

            }), 400

        # -------------------------------------------------
        # STEP 9: SAVE
        # -------------------------------------------------

        save_reminder(

            reminder_text,

            reminder_date,

            reminder_time

        )

        print(
            "VOICE REMINDER SAVED SUCCESSFULLY"
        )

        return jsonify({

            "success": True,

            "message":
                "Voice reminder added successfully.",

            "reminder": {

                "reminder_text":
                    reminder_text,

                "reminder_date":
                    reminder_date,

                "reminder_time":
                    reminder_time

            }

        })

    except Exception as e:

        print(
            "VOICE REMINDER ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                "Server error while processing voice reminder."

        }), 500


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    print("\n======================================")
    print("ALZHEIMER VOICE ASSISTANT")
    print("======================================")

    print(
        "Flask server starting..."
    )

    print(
        "Qwen model: qwen2.5:3b"
    )

    print(
        "Ollama: http://localhost:11434"
    )

    print(
        "======================================\n"
    )

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )