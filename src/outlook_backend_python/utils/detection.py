# Step detection and success monitoring
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from outlook_backend_python.utils.helpers import safe_run, sleep
from outlook_backend_python.helpers.browser import find_frame_with
from outlook_backend_python.handlers.captcha import detect_press_and_hold_captcha

# Step detection
def detect_step_any_frame(driver):
    """Detect current step in any frame"""
    email_sel = ['input[type="email"]', 'input[name="MemberName"]', '#MemberName']
    pass_sel = ['input[type="password"]', '#PasswordInput']
    name_sel = ['#firstNameInput', '#lastNameInput', 'input[name*="first"]', '#FirstName', 'input[name*="last"]', '#LastName']
    dob_sel = [
        'button#BirthMonthDropdown[role="combobox"]', 'button[name="BirthMonth"][role="combobox"]', 'button[aria-label="Birth month"][role="combobox"]',
        'button#BirthDayDropdown[role="combobox"]', 'button[name="BirthDay"][role="combobox"]', 'button[aria-label="Birth day"][role="combobox"]',
        'button#BirthYearDropdown[role="combobox"]', 'button[name="BirthYear"][role="combobox"]', 'button[aria-label="Birth year"][role="combobox"]',
        'select#BirthMonth', 'select[name*="month"]', 'input#BirthMonth', 'input[name*="month"]',
        'select#BirthDay', 'select[name*="day"]', 'input#BirthDay', 'input[name*="day"]',
        'select#BirthYear', 'select[name*="year"]', 'input#BirthYear', 'input[name*="year"]',
        'input[type="number"][name="BirthYear"]', '#floatingLabelInput21', 'input[aria-label="Birth year"]'
    ]

    res = find_frame_with(driver, email_sel)
    if res and res['frame']:
        return "email", res['frame']

    res = find_frame_with(driver, pass_sel)
    if res and res['frame']:
        return "password", res['frame']

    res = find_frame_with(driver, name_sel)
    if res and res['frame']:
        return "name", res['frame']

    res = find_frame_with(driver, dob_sel)
    if res and res['frame']:
        return "dob", res['frame']

    cap = detect_press_and_hold_captcha(driver)
    if cap:
        return "press_and_hold_captcha", driver

    href = safe_run(lambda: driver.current_url, '')
    if 'outlook.live.com/mail' in href.lower():
        return "mailbox", driver
    if 'account.microsoft.com' in href.lower():
        return "account", driver

    return "unknown", driver

def wait_for_initial_step(driver):
    """Wait for initial step to be detected"""
    from time import time
    t0 = time()
    while (time() - t0) * 1000 < 10000:  # 10 seconds
        step, _ = detect_step_any_frame(driver)
        if step != "unknown":
            return step
        sleep(60)
    
    step, _ = detect_step_any_frame(driver)
    return step

# Success detection
def wait_for_success(driver):
    """Wait for success detection"""
    from time import time
    t0 = time()
    while (time() - t0) * 1000 < 60000:  # 60 seconds
        ok = safe_run(lambda: driver.execute_script("""
            const href = location.href;
            if (/outlook\\.live\\.com\\/mail/i.test(href) || /account\\.microsoft\\.com/i.test(href)) return true;
            if (document.querySelector('[data-app-launcher-part-id], #O365_MainLink_NavMenu')) return true;
            return false;
        """), False)
        if ok:
            return True
        sleep(220)
    return False

__all__ = [
    'detect_step_any_frame',
    'wait_for_initial_step',
    'wait_for_success'
]
