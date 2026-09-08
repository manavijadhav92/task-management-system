"""
Plain-function validators for user input. Kept separate from serializers so
they're easy to unit test and reuse (e.g. re-validating email format if we
ever add "update profile").
"""

import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email_format(email):
    if not email or not EMAIL_RE.match(email):
        return "Enter a valid email address."
    return None


def validate_password_strength(password):
    if not password or len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
        return "Password must contain at least one letter and one number."
    return None


def validate_name(name):
    if not name or not name.strip():
        return "Name is required."
    return None
