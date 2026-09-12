import re
from datetime import datetime


def detect_reminder_intent(text):
    text = text.lower()

    reminder_words = [
        "reminder",
        "remind",
        "yaad dilana",
        "yaad dila",
        "laga do",
        "set karo",
        "set kar do",
        "reminder laga",
        "karna hai",
        "khana hai",
        "jana hai",
        "lena hai"
    ]

    for word in reminder_words:
        if word in text:
            return "create_reminder"

    return "general_conversation"


def has_time(text):
    patterns = [
        r'\b\d{1,2}:\d{2}\b',
        r'\b\d{1,2}\s*baje\b',
        r'\b\d{1,2}\s*(am|pm)\b'
    ]

    for pattern in patterns:
        if re.search(pattern, text.lower()):
            return True

    return False


def find_invalid_hour(text):
    patterns = [
        r'(\d{1,2})\s*baje\b',
        r'(\d{1,2})\s*(am|pm)\b'
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text.lower())

        for match in matches:
            if isinstance(match, tuple):
                value = match[0]
            else:
                value = match

            hour = int(value)

            if hour > 23:
                return hour

    return None


def validate_reminder_request(text, date_value, time_value):

    errors = []

    intent = detect_reminder_intent(text)

    # Normal conversation
    if intent != "create_reminder":
        errors.append("This is not a reminder request.")

    # Invalid hour in ORIGINAL user input
    invalid_hour = find_invalid_hour(text)

    if invalid_hour is not None:
        errors.append(
            f"Invalid hour in user input: {invalid_hour}"
        )

    # Time missing
    if not has_time(text):
        errors.append("Reminder time is missing.")

    # Task
    if not text.strip():
        errors.append("Reminder task is missing.")

    # Date
    try:
        datetime.strptime(date_value, "%Y-%m-%d")
    except ValueError:
        errors.append("Invalid date.")

    # Time
    try:
        datetime.strptime(time_value, "%H:%M")
    except ValueError:
        errors.append("Invalid time.")

    if errors:
        return False, errors

    return True, []


# =====================================
# TESTS
# =====================================

tests = [
    (
        "next day at 6 am set reminder",
        "2026-09-04",
        "18:00"
    ),

    (
        "i am doing coding",
        "",
        ""
    ),

    (
        "next day at 35 set reminder",
        "2026-09-04",
        "11:35"
    ),

    (
        "next day i go to hospital",
        "2026-09-04",
        ""
    ),

    (
        "Hello, kaise ho",
        "",
        ""
    )
]


for number, (text, date_value, time_value) in enumerate(tests, 1):

    print("\n==============================")
    print("TEST", number)
    print("User:", text)

    valid, errors = validate_reminder_request(
        text,
        date_value,
        time_value
    )

    if valid:
        print("✅ VALID REMINDER")
        print("save in database.")

    else:
        print("❌ REJECTED")
        print("not save in data save")

        for error in errors:
            print("⚠️", error)