#!/usr/bin/env python3
"""
Main entry point for Outlook account creation using SeleniumBase
"""

import sys
import time
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import modules
from outlook_backend_python.helpers.browser import configure_human_like_browser, frame_has_visible
from outlook_backend_python.utils.helpers import email_variations, numbered_email, random_dob, safe_run, human_pause, sleep
from outlook_backend_python.handlers.form import fill_email, fill_password, fill_name, fill_dob
from outlook_backend_python.handlers.captcha import handle_press_and_hold_captcha
from outlook_backend_python.utils.detection import detect_step_any_frame, wait_for_success, wait_for_initial_step
from outlook_backend_python.utils.storage import save_completed
from outlook_backend_python.utils.constants import (
    WAIT_NAV, WAIT_UI, PASSWORD, BROWSER_ARGS,
    OUTLOOK_SIGNUP_URL, ALTERNATE_SIGNUP_URL
)

# Main account creation function
async def create_outlook_account(first_name, last_name):
    # Initialize SeleniumBase driver
    driver = Driver(
        browser="chrome",
        headless=False,
        uc=True,  # Undetected Chrome
        incognito=True,
        agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        do_not_track=True,
        **BROWSER_ARGS
    )
    
    driver.set_window_size(1920, 1080)
    driver.set_page_load_timeout(WAIT_NAV / 1000)  # Convert ms to seconds
    
    # Configure human-like browser
    configure_human_like_browser(driver)
    
    completed = {"email": False, "password": False, "name": False, "dob": False}
    chosen_dob = random_dob(18, 40)
    chosen_prefix = None
    
    def get_step():
        return detect_step_any_frame(driver)
    
    try:
        print("Navigating to Outlook signup…")
        driver.get(OUTLOOK_SIGNUP_URL)
        
        first_step = wait_for_initial_step(driver)
        print(f"Initial step detected: {first_step}")
        
        # EMAIL selection
        variants = email_variations(first_name, last_name)
        for v in variants:
            step, frame = get_step()
            if step != "email" and frame and frame_has_visible(frame, 'button#idBtn_Back, a.backButton'):
                safe_run(lambda: frame.find_element(By.CSS_SELECTOR, 'button#idBtn_Back, a.backButton').click())
                human_pause(160, 60)
            
            print(f"Trying {v}@outlook.com")
            if fill_email(driver, v):
                chosen_prefix = v
                completed["email"] = True
                break
        
        if not chosen_prefix:
            chosen_prefix = numbered_email(first_name, last_name, 1)
            print(f"All variants taken; using {chosen_prefix}@outlook.com")
            step = get_step()[0]
            if step != "email":
                safe_run(lambda: driver.get(ALTERNATE_SIGNUP_URL))
                human_pause(250, 60)
            
            if fill_email(driver, chosen_prefix):
                completed["email"] = True
        
        # Step loop
        for i in range(20):
            step, _ = get_step()
            print(f"Current step: {step}")
            
            if step == "password" and not completed["password"]:
                print("Setting password…")
                fill_password(driver, PASSWORD)
                completed["password"] = True
                continue
            
            if step == "name" and not completed["name"]:
                print("Entering name…")
                fill_name(driver, first_name, last_name)
                completed["name"] = True
                continue
            
            if step == "dob" and not completed["dob"]:
                print("Filling DOB…")
                fill_dob(driver, chosen_dob, get_step)
                print(f"DOB used: {chosen_dob['day']}/{chosen_dob['month']}/{chosen_dob['year']}")
                completed["dob"] = True
                continue
            
            if step == "press_and_hold_captcha":
                success = handle_press_and_hold_captcha(driver, max_attempts=3)
                if success:
                    sleep(1500)
                continue
            
            if step in ["mailbox", "account"]:
                break
            
            sleep(700)
        
        # Success
        ok = wait_for_success(driver)
        if ok:
            print("Signup looks successful.")
            if chosen_prefix:
                save_completed(first_name, last_name, chosen_prefix, PASSWORD)
        else:
            print("Could not confirm success automatically. If the mailbox loaded, you can save manually.")
        
        print("Flow complete. Browser will remain open.")
        
    except Exception as err:
        print(f"Flow error: {err}")
        print("You can finish manually in the open browser.")
    
    finally:
        # Don't close the browser to allow manual inspection
        pass

# CLI interface
def main():
    if len(sys.argv) > 2:
        first_name = sys.argv[1]
        last_name = sys.argv[2]
    else:
        try:
            first_name = input("Enter first name: ")
            last_name = input("Enter last name: ")
        except Exception:
            first_name = ""
            last_name = ""

    # Ensure non-empty names
    if not first_name.strip():
        first_name = "John"
    if not last_name.strip():
        last_name = "Doe"

    print(f"Creating account for: {first_name} {last_name}")

    # Run the async function
    import asyncio
    asyncio.run(create_outlook_account(first_name, last_name))

if __name__ == "__main__":
    main()
