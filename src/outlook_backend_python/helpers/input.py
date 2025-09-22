# Input handling and form interaction helpers
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from outlook_backend_python.utils.helpers import safe_run, human_pause, sleep
from outlook_backend_python.utils.constants import MONTH_NAMES

# React-safe input helpers
def react_set_value(driver, element, value):
    """Set value in React-compatible way"""
    safe_run(lambda: driver.execute_script("""
        const el = arguments[0];
        const val = arguments[1];
        const descriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
        descriptor.set.call(el, String(val));
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
    """, element, str(value)))

def type_exact(driver, selector, value, verify_length=None):
    """Type exact value with verification"""
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        element.click()
        element.send_keys(Keys.CONTROL + 'a')  # Select all
        element.send_keys(Keys.BACKSPACE)      # Clear
        human_pause()
        
        react_set_value(driver, element, value)
        human_pause()
        
        if verify_length is not None:
            current_value = element.get_attribute('value') or ''
            if len(current_value) != verify_length:
                # Retry with keyboard typing
                element.click()
                element.send_keys(Keys.CONTROL + 'a')
                element.send_keys(Keys.BACKSPACE)
                human_pause()
                element.send_keys(str(value))
                human_pause()
                current_value = element.get_attribute('value') or ''
                return len(current_value) == verify_length
            
        return True
    except (NoSuchElementException, StaleElementReferenceException):
        return False

# Fluent UI dropdown helpers
def read_combobox_text(driver, button_selector):
    """Read text from combobox"""
    return safe_run(lambda: driver.execute_script("""
        const el = document.querySelector(arguments[0]);
        if (!el) return '';
        const span = el.querySelector('[data-testid="truncatedSelectedText"]') || el;
        return (span.textContent || '').trim();
    """, button_selector), '')

def select_fluent_dropdown_verified(driver, button_selector, text, max_retries=4, get_step=None):
    """Select from Fluent UI dropdown with verification"""
    attempt = 0
    wanted = (text or '').strip().lower()
    
    while attempt <= max_retries:
        attempt += 1
        
        if get_step:
            step, _ = get_step()
            if step != "dob":
                return "step-changed"
        
        try:
            button = driver.find_element(By.CSS_SELECTOR, button_selector)
            if not button.is_displayed():
                sleep(300)
                continue
                
            # Check if already expanded
            expanded = button.get_attribute('aria-expanded') == 'true'
            if not expanded:
                button.click()
                sleep(200)
            
            # Wait for listbox
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            WebDriverWait(driver, 4).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[role="listbox"]'))
            )
            
            # Find options
            listboxes = driver.find_elements(By.CSS_SELECTOR, 'div[role="listbox"]')
            if not listboxes:
                sleep(300)
                continue
                
            listbox = listboxes[-1]
            options = listbox.find_elements(By.CSS_SELECTOR, '[role="option"]')
            
            if not options:
                sleep(300)
                continue
            
            # Find target option
            target = None
            for option in options:
                label = (option.text or '').strip().lower()
                if label == wanted or wanted in label:
                    target = option
                    break
            
            if not target:
                sleep(300)
                continue
            
            # Hover and click
            from selenium.webdriver import ActionChains
            ActionChains(driver).move_to_element(target).pause(0.09).click(target).perform()
            sleep(220)
            
            # Verify selection
            current = read_combobox_text(driver, button_selector).lower()
            if wanted in current:
                return True
                
            # Escape and retry
            button.send_keys(Keys.ESCAPE)
            sleep(300)
            
        except Exception:
            sleep(300)
            continue
    
    raise Exception(f"Failed to set combobox {button_selector} to '{text}' after {max_retries} retries")

# DOB field helpers
def wait_for_dob_ready(driver):
    """Wait for DOB fields to be ready"""
    from time import time
    t0 = time()
    
    while (time() - t0) * 1000 < 12000:
        ready = safe_run(lambda: driver.execute_script("""
            const pick = (s) => document.querySelector(s);
            const monthBtn = pick('button#BirthMonthDropdown, button[name="BirthMonth"][role="combobox"], button[aria-label="Birth month"][role="combobox"]');
            const dayBtn   = pick('button#BirthDayDropdown,   button[name="BirthDay"][role="combobox"],   button[aria-label="Birth day"][role="combobox"]');
            const yearInp  = pick('input[type="number"][name="BirthYear"], #floatingLabelInput21, input[aria-label="Birth year"], input[name*="year"], #BirthYear');
            
            const vis = (el) => {
                if (!el) return false;
                const st = getComputedStyle(el);
                if (st.display === 'none' || st.visibility === 'hidden' || st.opacity === '0') return false;
                if (el.getAttribute('aria-hidden') === 'true') return false;
                const rects = el.getClientRects();
                return rects && rects.length > 0;
            };
            
            const nd = (el) => el && !el.hasAttribute('disabled') && el.getAttribute('aria-disabled') !== 'true';
            
            return vis(monthBtn) && vis(dayBtn) && vis(yearInp) && nd(monthBtn) && nd(dayBtn) && nd(yearInp);
        """), False)
        
        if ready:
            return True
        sleep(150)
    
    return False

def set_dob_field(driver, native_select, fluent_button, input_selector, value_as_string, verify_digits=None):
    """Set DOB field with appropriate method"""
    from outlook_backend_python.helpers.browser import frame_has_visible
    
    if native_select and frame_has_visible(driver, native_select):
        try:
            from selenium.webdriver.support.ui import Select
            select = Select(driver.find_element(By.CSS_SELECTOR, native_select))
            select.select_by_visible_text(value_as_string)
            human_pause()
            return True
        except Exception:
            pass
    
    if fluent_button and frame_has_visible(driver, fluent_button):
        try:
            result = select_fluent_dropdown_verified(driver, fluent_button, value_as_string)
            if result == "step-changed":
                return True
            human_pause(250, 60)
            return True
        except Exception:
            pass
    
    if input_selector and frame_has_visible(driver, input_selector):
        if verify_digits:
            ok = type_exact(driver, input_selector, value_as_string, verify_length=verify_digits)
            sleep(200)
            human_pause(250, 60)
            return ok
        else:
            try:
                element = driver.find_element(By.CSS_SELECTOR, input_selector)
                element.click()
                element.send_keys(Keys.CONTROL + 'a')
                react_set_value(driver, element, value_as_string)
                sleep(200)
                human_pause(250, 60)
                return True
            except Exception:
                pass
    
    return False

__all__ = [
    'react_set_value',
    'type_exact',
    'read_combobox_text',
    'select_fluent_dropdown_verified',
    'wait_for_dob_ready',
    'set_dob_field'
]
