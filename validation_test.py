from datetime import datetime


def validate_reminder(reminder_text, reminder_date, reminder_time):
    errors = []

    # Task check
    if not reminder_text or not reminder_text.strip():
        errors.append("Reminder task missing.")

    # Date check
    try:
        datetime.strptime(reminder_date, "%Y-%m-%d")
    except ValueError:
        errors.append("Invalid date.")

    # Time check
    try:
        datetime.strptime(reminder_time, "%H:%M")
    except ValueError:
        errors.append("Invalid time.")

    if errors:
        return False, errors

    return True, []


# Test 1: Valid reminder
print("TEST 1")
valid, errors = validate_reminder(
    "dawa khani hai",
    "2026-09-03",
    "08:00"
)

print("Valid:", valid)
print("Errors:", errors)


# Test 2: Invalid time
print("\nTEST 2")
valid, errors = validate_reminder(
    "doctor ke paas jana hai",
    "2026-09-03",
    "35:00"
)

print("Valid:", valid)
print("Errors:", errors)