import sqlite3
import time
from datetime import datetime
import subprocess
import winsound

from windows_toasts import Toast, WindowsToaster


# ==========================================
# SPEAKER
# ==========================================

def speak_reminder(text):
    """
    Windows SAPI ke through reminder ko clearly speak karta hai.
    """

    # PowerShell apostrophe safe karna
    safe_text = text.replace("'", "''")

    command = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$s.Rate = -3; "
        f"$s.Speak('{safe_text}'); "
        "$s.Dispose()"
    )

    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            command
        ],
        check=False
    )


# ==========================================
# WINDOWS NOTIFICATION
# ==========================================

def show_notification(text):
    """
    Windows 10/11 toast notification show karta hai.
    """

    toaster = WindowsToaster(
        "Alzheimer Voice Assistant"
    )

    toast = Toast()

    toast.text_fields = [
        "🔔 Alzheimer Voice Assistant",
        "Reminder",
        text
    ]

    toaster.show_toast(toast)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    """
    SQLite database connection return karta hai.
    """
    return sqlite3.connect("reminders.db")


# ==========================================
# REMINDER SYSTEM START
# ==========================================

print()
print("🔔 Alzheimer Voice Assistant")
print("==========================================")
print("⏰ Real-time reminder checker started.")
print("🔊 Voice + 🔔 Notification + Beep active.")
print("❌ Stop karne ke liye Ctrl + C dabao.")
print("==========================================")
print()


# ==========================================
# REAL-TIME CHECKING
# ==========================================

try:

    while True:

        # ----------------------------------
        # CURRENT DATE & TIME
        # ----------------------------------

        now = datetime.now()

        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")


        # ----------------------------------
        # DATABASE OPEN
        # ----------------------------------

        connection = get_connection()
        cursor = connection.cursor()


        # ----------------------------------
        # FIND DUE REMINDERS
        # ----------------------------------

        cursor.execute(
            """
            SELECT
                id,
                reminder_text,
                repeat_count
            FROM reminders
            WHERE reminder_date = ?
            AND reminder_time = ?
            AND completed = 0
            """,
            (
                current_date,
                current_time
            )
        )

        reminders = cursor.fetchall()


        # ----------------------------------
        # PROCESS REMINDERS
        # ----------------------------------

        for reminder in reminders:

            reminder_id = reminder[0]
            reminder_text = reminder[1]

            # Agar repeat_count empty ho
            # to default 1 use hoga
            repeat_count = reminder[2] or 1


            print()
            print("🔔 =====================================")
            print("🔔 REMINDER TIME MATCHED!")
            print("📝 Task:", reminder_text)
            print("📅 Date:", current_date)
            print("⏰ Time:", current_time)
            print("🔊 Repeat:", repeat_count, "times")
            print("🔔 =====================================")


            # ----------------------------------
            # WINDOWS NOTIFICATION
            # ----------------------------------

            try:

                print("🔔 Sending Windows notification...")

                show_notification(
                    "Reminder: " + reminder_text
                )

                print("✅ Notification sent.")

            except Exception as e:

                print(
                    "⚠️ Notification error:",
                    e
                )


            # ----------------------------------
            # BEEP + VOICE
            # ----------------------------------

            for i in range(repeat_count):

                print(
                    f"🔊 Speaking {i + 1}/{repeat_count}"
                )

                # Beep
                try:

                    winsound.Beep(
                        1000,
                        500
                    )

                except Exception as e:

                    print(
                        "⚠️ Beep error:",
                        e
                    )


                # Voice
                try:

                    speak_reminder(
                        "Reminder. " + reminder_text
                    )

                except Exception as e:

                    print(
                        "⚠️ Voice error:",
                        e
                    )


                # 3 second gap
                if i < repeat_count - 1:

                    time.sleep(3)


            # ----------------------------------
            # MARK REMINDER COMPLETED
            # ----------------------------------

            cursor.execute(
                """
                UPDATE reminders
                SET completed = 1
                WHERE id = ?
                """,
                (
                    reminder_id,
                )
            )

            connection.commit()


            print("✅ Reminder completed.")
            print()


        # ----------------------------------
        # CLOSE DATABASE
        # ----------------------------------

        connection.close()


        # ----------------------------------
        # CHECK EVERY 5 SECONDS
        # ----------------------------------

        time.sleep(5)


# ==========================================
# STOP WITH CTRL + C
# ==========================================

except KeyboardInterrupt:

    print()
    print("🛑 Reminder checker stopped.")
    print("👋 Alzheimer Voice Assistant closed.")


# ==========================================
# OTHER ERRORS
# ==========================================

except Exception as e:

    print()
    print("❌ Reminder system error:")
    print(e)