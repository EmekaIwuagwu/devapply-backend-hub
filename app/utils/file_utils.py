import base64
import re


def validate_base64(base64_string):
    """Validate if string is valid base64"""
    try:
        # Remove data URL prefix if present (e.g., "data:image/png;base64,")
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]

        # Try to decode
        base64.b64decode(base64_string)
        return True, base64_string
    except Exception as e:
        return False, None


def get_file_size_from_base64(base64_string):
    """Calculate file size from base64 string"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]

        # Calculate size (base64 is ~33% larger than original)
        padding = base64_string.count('=')
        size = (len(base64_string) * 3) / 4 - padding
        return int(size)
    except Exception:
        return 0


def get_file_extension(filename):
    """Extract file extension from filename"""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return None


def clean_base64(base64_string):
    """Remove data URL prefix from base64 string"""
    if ',' in base64_string:
        return base64_string.split(',')[1]
    return base64_string
