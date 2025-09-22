# Constants and configuration

# Timings
WAIT_NAV = 45000  # milliseconds
WAIT_UI = 15000   # milliseconds
STARTUP_WAIT_MS = 10000

ACTION_DELAY_MS = 120
ACTION_JITTER_MS = 80
BETWEEN_FIELDS_DELAY_MS = 250
DROPDOWN_OPEN_SETTLE_MS = 200
DROPDOWN_SELECT_SETTLE_MS = 220
INPUT_VERIFICATION_WAIT_MS = 200

# DOB pacing / robustness
DOB_READY_TIMEOUT_MS = 12000
DOB_POST_SELECT_WAIT_MS = 320
DOB_RETRY_PAUSE_MS = 300
DOB_MAX_RETRIES = 4

# NAME pacing / robustness
NAME_READY_TIMEOUT_MS = 14000
NAME_VERIFY_WAIT_MS = 200

# Default password
PASSWORD = 'SecurePass123!'

# Browser arguments for SeleniumBase
BROWSER_ARGS = {
    'no_sandbox': True,
    'disable_features': 'IsolateOrigins,site-per-process',
    'disable_gpu': True,
    'window_size': '1920,1080'
}

# URLs
OUTLOOK_SIGNUP_URL = 'https://outlook.live.com/mail/0/?prompt=create_account'
ALTERNATE_SIGNUP_URL = 'https://signup.live.com/signup'

# Month names for dropdown selection
MONTH_NAMES = ['', 'January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']
