
import re

def detect_language(code):
    if code and code.startswith('ar'):
        return 'ar'
    return 'en'

def is_valid_query(text):
    return text and len(text.strip()) >= 2
