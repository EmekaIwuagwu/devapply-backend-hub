import re
from email_validator import validate_email as validate_email_format, EmailNotValidError


def validate_email(email):
    """Validate email format"""
    try:
        validate_email_format(email)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)


def validate_password(password):
    """
    Validate password strength
    Requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    - At least 1 special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, None


def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return True, None

    # Basic phone validation (10-15 digits with optional + and spaces/dashes)
    pattern = r'^\+?[\d\s\-]{10,15}$'
    if not re.match(pattern, phone):
        return False, "Invalid phone number format"

    return True, None


def validate_skills(skills):
    """Validate skills array"""
    if not isinstance(skills, list):
        return False, "Skills must be an array"

    if len(skills) > 20:
        return False, "Maximum 20 skills allowed"

    for skill in skills:
        if not isinstance(skill, str):
            return False, "Each skill must be a string"
        if len(skill) > 50:
            return False, "Each skill must be maximum 50 characters"

    return True, None


def validate_file_size(size_bytes, max_size):
    """Validate file size"""
    if size_bytes > max_size:
        max_mb = max_size / (1024 * 1024)
        return False, f"File size exceeds maximum allowed size of {max_mb}MB"
    return True, None


def validate_file_type(file_type, allowed_types):
    """Validate file type"""
    if file_type.lower() not in allowed_types:
        return False, f"File type must be one of: {', '.join(allowed_types)}"
    return True, None
