# Form filling handlers
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from outlook_backend_python.utils.helpers import safe_run, human_pause, sleep
from outlook_backend_python.helpers.browser import wait_in_any_frame, click_next_in_frame, frame_has_visible
from outlook_backend_python.helpers.input import react_set_value, type_exact, wait_for_dob_ready, set_dob_field, select_fluent_dropdown_verified
from outlook_backend_python.handlers.captcha import wait_for_and_solve_press_hold
from outlook_backend_python.utils.constants import MONTH_NAMES

# Email filling
def fill_email(driver, email_prefix):
    """Fill email field and check availability"""
    try:
        res = wait_in_any_frame(driver, ['input[type="email"]', 'input[name="MemberName"]', '#MemberName'], 10000)
        if not res or not res['frame']:
            raise Exception("Email field not found")
        
        frame = res['frame']
        selector = res['selector']
        
        field = frame.find_element(By.CSS_SELECTOR, selector)
        if not field:
            raise Exception("Email field vanished")
        
        # Clear field
        field.click()
        field.send_keys(Keys.CONTROL + 'a')
        react_set_value(frame, field, '')
        human_pause()
        
        # Focus and set value
        field.click()
        react_set_value(frame, field, email_prefix)
        human_pause()
        
        # Click next
        click_next_in_frame(frame)
        
        # Check for error
        err_sel = safe_run(lambda: frame.execute_script("""
            const sels = ['[data-bind*="error"]','[role="alert"]','.error','.errorMessage','#usernameError'];
            for (const s of sels) {
                const el = document.querySelector(s);
                if (el && getComputedStyle(el).display !== 'none') return s;
            }
            return null;
        """), None)
        
        if err_sel:
            txt = safe_run(lambda: frame.find_element(By.CSS_SELECTOR, err_sel).text.lower(), '')
            if any(word in txt for word in ['taken', 'already', 'not available']):
                return False
                
        return True
        
    except Exception as e:
        print(f"Email filling error: {e}")
        return False

# Password filling
def fill_password(driver, password):
    """Fill password field"""
    try:
        res = wait_in_any_frame(driver, ['input[type="password"]', '#PasswordInput'], 10000)
        if not res or not res['frame']:
            raise Exception("Password field not found")
        
        frame = res['frame']
        selector = res['selector']
        
        field = frame.find_element(By.CSS_SELECTOR, selector)
        field.click()
        field.send_keys(Keys.CONTROL + 'a')
        human_pause()
        
        # Type password with delay
        for char in password:
            field.send_keys(char)
            sleep(15)
        
        human_pause()
        click_next_in_frame(frame)
        return True
        
    except Exception as e:
        print(f"Password filling error: {e}")
        return False

# Name filling
def fill_name(driver, first_name, last_name):
    """Fill name fields"""
    try:
        res = wait_in_any_frame(driver, ['#firstNameInput', '#lastNameInput'], 14000)
        if not res or not res['frame']:
            raise Exception("Name fields not found")
        
        frame = res['frame']
        
        # Wait for fields to be ready
        ready = False
        from time import time
        t0 = time()
        while (time() - t0) * 1000 < 14000:
            ready = safe_run(lambda: frame.execute_script("""
                const fn = document.querySelector('#firstNameInput');
                const ln = document.querySelector('#lastNameInput');
                const vis = (el) => {
                    if (!el) return false;
                    const st = getComputedStyle(el);
                    if (st.display === 'none' || st.visibility === 'hidden' || st.opacity === '0') return false;
                    if (el.getAttribute('aria-hidden') === 'true') return false;
                    const rects = el.getClientRects();
                    return rects && rects.length > 0;
                };
                const nd = (el) => el && !el.hasAttribute('disabled') && el.getAttribute('aria-disabled') !== 'true';
                return vis(fn) && vis(ln) && nd(fn) && nd(ln);
            """), False)
            
            if ready:
                break
            sleep(120)
        
        if not ready:
            raise Exception("Name inputs not ready")
        
        # Fill first name
        f_sel = '#firstNameInput'
        f_field = frame.find_element(By.CSS_SELECTOR, f_sel)
        # Robustly select all text (triple click)
        for _ in range(3):
            f_field.click()
            sleep(30)
        react_set_value(frame, f_field, '')
        human_pause()
        react_set_value(frame, f_field, first_name)
        sleep(200)
        
        # Verify first name
        first_ok = safe_run(lambda: frame.find_element(By.CSS_SELECTOR, f_sel).get_attribute('value').strip() != '', False)
        if not first_ok:
            f_field.click()
            f_field.send_keys(Keys.CONTROL + 'a')
            react_set_value(frame, f_field, '')
            human_pause()
            for char in first_name:
                f_field.send_keys(char)
                sleep(15)
            sleep(200)
        
        # Fill last name
        l_sel = '#lastNameInput'
        l_field = frame.find_element(By.CSS_SELECTOR, l_sel)
        # Robustly select all text (triple click)
        for _ in range(3):
            l_field.click()
            sleep(30)
        react_set_value(frame, l_field, '')
        human_pause()
        react_set_value(frame, l_field, last_name)
        sleep(200)
        
        # Verify last name
        last_ok = safe_run(lambda: frame.find_element(By.CSS_SELECTOR, l_sel).get_attribute('value').strip() != '', False)
        if not last_ok:
            l_field.click()
            l_field.send_keys(Keys.CONTROL + 'a')
            react_set_value(frame, l_field, '')
            human_pause()
            for char in last_name:
                l_field.send_keys(char)
                sleep(15)
            sleep(200)
        
        human_pause(200, 60)
        click_next_in_frame(frame)
        
        # Handle press-and-hold challenge after Name
        print("Checking for press-and-hold challenge after Name…")
        solved_now = wait_for_and_solve_press_hold(driver, appear_timeout_ms=25000, max_attempts=3)
        if solved_now:
            sleep(1500)
            
        return True
        
    except Exception as e:
        print(f"Name filling error: {e}")
        return False

# Date of birth filling
def fill_dob(driver, dob, get_step):
    """Fill date of birth fields"""
    try:
        res = wait_in_any_frame(driver, [
            'button#BirthMonthDropdown', 'button[name="BirthMonth"][role="combobox"]', 'button[aria-label="Birth month"][role="combobox"]',
            'select#BirthMonth', 'select[name*="month"]', 'input#BirthMonth', 'input[name*="month"]'
        ], 10000)
        
        if not res or not res['frame']:
            raise Exception("DOB fields not found")
        
        frame = res['frame']
        day, month, year = dob['day'], dob['month'], dob['year']
        
        wait_for_dob_ready(frame)
        
        # Month selection
        month_btn_sel = 'button#BirthMonthDropdown, button[name="BirthMonth"][role="combobox"], button[aria-label="Birth month"][role="combobox"]'
        month_native_sel = 'select[name*="month"], #BirthMonth'
        
        if frame_has_visible(frame, month_native_sel):
            from selenium.webdriver.support.ui import Select
            select = Select(frame.find_element(By.CSS_SELECTOR, month_native_sel))
            select.select_by_visible_text(MONTH_NAMES[month])
            human_pause(320, 40)
        else:
            result = select_fluent_dropdown_verified(frame, month_btn_sel, MONTH_NAMES[month], get_step=get_step)
            if result == "step-changed":
                return
        
        # Day selection
        day_btn_sel = 'button#BirthDayDropdown, button[name="BirthDay"][role="combobox"], button[aria-label="Birth day"][role="combobox"]'
        day_native_sel = 'select[name*="day"], #BirthDay'
        
        if frame_has_visible(frame, day_native_sel):
            from selenium.webdriver.support.ui import Select
            select = Select(frame.find_element(By.CSS_SELECTOR, day_native_sel))
            select.select_by_visible_text(str(day))
            human_pause(320, 40)
        else:
            result = select_fluent_dropdown_verified(frame, day_btn_sel, str(day), get_step=get_step)
            if result == "step-changed":
                return
        
        # Year selection
        year_selectors = [
            'input[type="number"][name="BirthYear"]',
            '#floatingLabelInput21',
            'input[aria-label="Birth year"]',
            'input[name*="year"]',
            '#BirthYear'
        ]
        
        year_sel_visible = None
        for sel in year_selectors:
            if frame_has_visible(frame, sel):
                year_sel_visible = sel
                break
        
        if year_sel_visible:
            ok = type_exact(frame, year_sel_visible, str(year), verify_length=4)
            human_pause(320, 40)
            if not ok:
                raise Exception("Year input did not accept 4 digits")
        else:
            ok = set_dob_field(frame, {
                'native_select': 'select[name*="year"], #BirthYear',
                'fluent_button': 'button#BirthYearDropdown, button[name="BirthYear"][role="combobox"], button[aria-label="Birth year"][role="combobox"]',
                'input_selector': ','.join(year_selectors),
                'value_as_string': str(year),
                'verify_digits': 4,
            })
            if not ok:
                raise Exception("Could not set Year")
        
        click_next_in_frame(frame)
        return True
        
    except Exception as e:
        print(f"DOB filling error: {e}")
        return False

__all__ = [
    'fill_email',
    'fill_password',
    'fill_name',
    'fill_dob'
]
