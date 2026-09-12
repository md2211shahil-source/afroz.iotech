import re


def extract_time(user_text):
    if not user_text:
        return None

    text = user_text.lower().strip()

    # =========================================================
    # 1. AM / PM FORMAT
    # Examples:
    # 11:46 PM -> 23:46
    # 11:46 AM -> 11:46
    # 8 PM     -> 20:00
    # 8 AM     -> 08:00
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
    # 2. 24-HOUR HH:MM FORMAT
    # Examples:
    # 08:30 -> 08:30
    # 14:45 -> 14:45
    # 23:59 -> 23:59
    # =========================================================

    match = re.search(r"\b(\d{1,2}):(\d{2})\b", text)

    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))

        if hour > 23 or minute > 59:
            return None

        return f"{hour:02d}:{minute:02d}"

    # =========================================================
    # 3. HINGLISH / HINDI "BAJE"
    # Examples:
    # 8 baje
    # 8 baje subah
    # 8 baje raat
    # 8:30 baje
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

        if any(word in text for word in ["subha", "subah", "morning"]):
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
    # Examples:
    # at 8 -> 08:00
    # at 14 -> 14:00
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