from datetime import datetime
import re


def validate_reminder(
    reminder_text,
    reminder_date,
    reminder_time,
    user_text=""
):
    errors = []

    # ---------------------------------------------------------
    # TASK VALIDATION
    # ---------------------------------------------------------

    if not reminder_text or not reminder_text.strip():
        errors.append("Reminder task missing.")

    # ---------------------------------------------------------
    # DATE VALIDATION
    # ---------------------------------------------------------

    if not reminder_date or not reminder_date.strip():
        errors.append("Reminder date missing.")
    else:
        try:
            datetime.strptime(reminder_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Invalid date.")

    # ---------------------------------------------------------
    # FINAL TIME VALIDATION
    # ---------------------------------------------------------

    if not reminder_time or not reminder_time.strip():
        errors.append("Reminder time is required.")
    else:
        try:
            datetime.strptime(reminder_time, "%H:%M")
        except ValueError:
            errors.append("Invalid time.")

    # ---------------------------------------------------------
    # EXTRACT TIME DIRECTLY FROM USER INPUT
    # ---------------------------------------------------------

    user_time = extract_user_time(user_text)

    if user_time is None:
        errors.append("A valid time is required in the user's input.")

    # ---------------------------------------------------------
    # AI TIME MUST MATCH USER TIME
    # ---------------------------------------------------------

    if user_time and reminder_time:
        if user_time != reminder_time:
            errors.append("AI time does not match user's time.")

    # ---------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------

    if errors:
        return False, errors

    return True, []


def extract_user_time(user_text):
    if not user_text:
        return None

    text = user_text.lower().strip()

    # =========================================================
    # 1. AM / PM MUST BE CHECKED FIRST
    # =========================================================

    match = re.search(
        r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b",
        text
    )

    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        period = match.group(3)

        if hour < 1 or hour > 12:
            return None

        if minute > 59:
            return None

        if period == "am":
            if hour == 12:
                hour = 0
        else:
            if hour < 12:
                hour += 12

        return f"{hour:02d}:{minute:02d}"

    # =========================================================
    # 2. HH:MM 24-HOUR FORMAT
    # =========================================================

    match = re.search(
        r"\b(\d{1,2}):(\d{2})\b",
        text
    )

    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))

        if hour > 23 or minute > 59:
            return None

        return f"{hour:02d}:{minute:02d}"

    # =========================================================
    # 3. HINGLISH "BAJE"
    # =========================================================

    match = re.search(
        r"\b(\d{1,2})(?::(\d{2}))?\s*baje\b",
        text
    )

    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0

        if hour > 23 or minute > 59:
            return None

        if any(
            word in text
            for word in ["subha", "subah", "morning"]
        ):
            if hour == 12:
                hour = 0

        elif any(
            word in text
            for word in ["raat", "shaam", "sham", "evening", "night"]
        ):
            if hour < 12:
                hour += 12

        return f"{hour:02d}:{minute:02d}"

    # =========================================================
    # 4. ENGLISH "AT 8"
    # =========================================================

    match = re.search(
        r"\bat\s+(\d{1,2})(?::(\d{2}))?\b",
        text
    )

    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0

        if hour > 23 or minute > 59:
            return None

        return f"{hour:02d}:{minute:02d}"

    return None