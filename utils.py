import hashlib
import re
from datetime import datetime

def hash_file(file_content):
    """
    Generate hash of file content for deduplication
    """
    return hashlib.sha256(file_content).hexdigest()

def sanitize_filename(filename):
    """
    Sanitize filename for safe storage
    """
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Remove dangerous characters
    filename = re.sub(r'[^\w\s\-\.]', '', filename)
    
    # Limit length
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + ('.' + ext if ext else '')
    
    return filename

def format_timestamp(dt=None):
    """
    Format datetime for API responses
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + 'Z'

def truncate_text(text, max_length=200, suffix='...'):
    """
    Truncate text to max length
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def extract_numbers(text):
    """
    Extract all numbers from text
    """
    return [int(n) for n in re.findall(r'\d+', text)]

def calculate_percentage(part, total):
    """
    Calculate percentage safely
    """
    if total == 0:
        return 0
    return round((part / total) * 100, 2)

def validate_file_size(file_bytes, max_size_mb=10):
    """
    Check if file size is within limit
    """
    size_mb = len(file_bytes) / (1024 * 1024)
    return size_mb <= max_size_mb

def normalize_whitespace(text):
    """
    Normalize whitespace in text
    """
    return ' '.join(text.split())

def contains_any(text, keywords):
    """
    Check if text contains any of the keywords
    """
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)

def get_file_extension(filename):
    """
    Get file extension safely
    """
    if '.' not in filename:
        return ''
    return '.' + filename.rsplit('.', 1)[1].lower()

def format_risk_badge(risk_level):
    """
    Format risk level for display
    """
    badges = {
        'low': '🟢 Low Risk',
        'medium': '🟡 Medium Risk',
        'high': '🟠 High Risk',
        'critical': '🔴 Critical Risk'
    }
    return badges.get(risk_level, '⚪ Unknown')

def parse_duration(text):
    """
    Parse duration from text (e.g., "6 months", "2 years")
    Returns duration in days
    """
    text_lower = text.lower()
    
    # Extract number
    numbers = re.findall(r'(\d+)', text_lower)
    if not numbers:
        return None
    
    value = int(numbers[0])
    
    # Determine unit
    if 'day' in text_lower:
        return value
    elif 'week' in text_lower:
        return value * 7
    elif 'month' in text_lower:
        return value * 30
    elif 'year' in text_lower:
        return value * 365
    
    return None

def log_event(event_type, details):
    """
    Simple event logging
    """
    timestamp = format_timestamp()
    print(f"[{timestamp}] {event_type}: {details}")

def create_error_response(error_message, status_code=400):
    """
    Create standardized error response
    """
    return {
        "error": error_message,
        "status_code": status_code,
        "timestamp": format_timestamp()
    }

def create_success_response(data, message=None):
    """
    Create standardized success response
    """
    response = {
        "success": True,
        "data": data,
        "timestamp": format_timestamp()
    }
    if message:
        response["message"] = message
    return response