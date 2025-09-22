# Utility functions
import time
import random
from .constants import ACTION_DELAY_MS, ACTION_JITTER_MS

# Tiny utils
def sleep(ms):
    """Sleep for milliseconds"""
    time.sleep(ms / 1000)

def jitter(base, j):
    """Add jitter to a base value"""
    return base + random.randint(-j, j)

def human_pause(base=ACTION_DELAY_MS, j=ACTION_JITTER_MS):
    """Human-like pause with jitter"""
    sleep(jitter(base, j))

def safe_run(fn, fallback=None):
    """Safely run a function and return fallback on error"""
    try:
        return fn()
    except Exception:
        return fallback

# Email generation functions
def email_variations(first_name, last_name):
    """Generate email variations"""
    f = first_name.lower()
    l = last_name.lower()
    i = f[0]
    return [
        f"{f}.{l}", f"{i}.{l}", f"{f}{l}", f"{i}{l}",
        f"{l}.{f}", f"{l}{f}", f"{f}_{l}", f"{i}_{l}"
    ]

def numbered_email(first_name, last_name, n):
    """Generate numbered email"""
    return f"{first_name.lower()}.{last_name.lower()}{n}"

# Date of birth generation
def random_dob(min_age, max_age):
    """Generate random date of birth"""
    from datetime import datetime
    current_year = datetime.now().year
    min_year = current_year - max_age
    max_year = current_year - min_age
    
    year = random.randint(min_year, max_year)
    month = random.randint(1, 12)
    
    # Get max days in month
    if month == 2:
        # February - check for leap year
        max_day = 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:
        max_day = 31
    
    day = random.randint(1, max_day)
    return {"day": day, "month": month, "year": year}

# Month names for dropdown selection (imported from constants)
from .constants import MONTH_NAMES

__all__ = [
    'sleep',
    'jitter',
    'human_pause',
    'safe_run',
    'email_variations',
    'numbered_email',
    'random_dob',
    'MONTH_NAMES'
]
