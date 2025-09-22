# Captcha handling functionality
import pyautogui
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from ..utils.helpers import safe_run, human_pause, sleep

# Try to find a press-and-hold button
import re

def find_hold_button(driver):
    """Find press-and-hold button (robust, regex-based)"""
    try:
        # 1) role=button or button with text/aria-label matching regex
        elements = driver.find_elements(By.CSS_SELECTOR, '[role="button"], button')
        pattern = re.compile(r'press\s*&?\s*hold', re.I)
        for element in elements:
            text = (element.text or '').strip().lower()
            aria_label = (element.get_attribute('aria-label') or '').strip().lower()
            if pattern.search(text) or pattern.search(aria_label):
                return element

        # 2) aria-label contains press & hold (case-insensitive)
        elements = driver.find_elements(By.CSS_SELECTOR, '*[role="button"][aria-label*="press" i][aria-label*="hold" i], button[aria-label*="press" i][aria-label*="hold" i]')
        if elements:
            return elements[0]

        # 3) fallback: any visible clickable, prefer those with text clues
        elements = driver.find_elements(By.CSS_SELECTOR, 'button, [role="button"], .btn, .button')
        visible_elements = []
        for element in elements:
            try:
                if element.is_displayed():
                    visible_elements.append(element)
            except:
                continue

        # Prefer visible elements with text/aria-label clue
        for element in visible_elements:
            text = (element.text or '').strip().lower()
            aria_label = (element.get_attribute('aria-label') or '').strip().lower()
            if pattern.search(text) or pattern.search(aria_label):
                return element

        # Sort by size (largest first)
        visible_elements.sort(key=lambda e: e.size['width'] * e.size['height'], reverse=True)
        if visible_elements:
            return visible_elements[0]

    except Exception:
        pass

    return None

# Get absolute center point of an element
def get_absolute_center_point(driver, element):
    """Get absolute center point of element on screen"""
    try:
        # Get element location and size
        location = element.location
        size = element.size
        
        # Calculate center
        x = location['x'] + size['width'] / 2
        y = location['y'] + size['height'] / 2
        
        # Adjust for browser chrome and scrolling
        window_position = driver.get_window_position()
        x += window_position['x']
        y += window_position['y']
        
        return {'x': int(x), 'y': int(y)}
        
    except Exception:
        return None

# Get press-and-hold context
def get_press_hold_context(driver):
    """Get context for press-and-hold captcha"""
    try:
        # Check iframes first
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        for iframe in iframes:
            try:
                # Switch to iframe
                driver.switch_to.frame(iframe)
                
                # Check for press-and-hold clues
                has_clue = safe_run(lambda: driver.execute_script("""
                    const t = (document.body.textContent || '').toLowerCase();
                    const clue = t.includes('press and hold') || t.includes('press & hold');
                    const barCandidate = Array.from(document.querySelectorAll('div[style*="width"],span[style*="width"]'))
                        .some(el => /width:\\s*\\d+(?:\\.\\d+)?px/i.test(el.getAttribute('style') || ''));
                    return clue || barCandidate;
                """), False)
                
                if has_clue:
                    btn = find_hold_button(driver)
                    if btn:
                        point = get_absolute_center_point(driver, btn)
                        if point:
                            return {'frame': driver, 'click_point': point, 'btn': btn}
                    
                    # Fallback: center of iframe
                    location = iframe.location
                    size = iframe.size
                    if location and size:
                        window_position = driver.get_window_position()
                        x = location['x'] + size['width'] / 2 + window_position['x']
                        y = location['y'] + size['height'] / 2 + window_position['y']
                        return {'frame': driver, 'click_point': {'x': int(x), 'y': int(y)}, 'btn': None}
                        
            except Exception:
                continue
            finally:
                driver.switch_to.default_content()
        
        # Check main page
        btn = find_hold_button(driver)
        if btn:
            point = get_absolute_center_point(driver, btn)
            if point:
                return {'frame': driver, 'click_point': point, 'btn': None}
        
        # Check containers
        containers = driver.find_elements(By.CSS_SELECTOR, '#px-captcha, [id*="captcha" i], [class*="captcha" i]')
        for container in containers:
            try:
                if container.is_displayed():
                    point = get_absolute_center_point(driver, container)
                    if point:
                        return {'frame': driver, 'click_point': point, 'btn': None}
            except:
                continue
        
        # Fallback to viewport center
        window_size = driver.get_window_size()
        window_position = driver.get_window_position()
        x = window_position['x'] + window_size['width'] / 2
        y = window_position['y'] + window_size['height'] / 2
        return {'frame': driver, 'click_point': {'x': int(x), 'y': int(y)}, 'btn': None}
        
    except Exception:
        return None

# Detect press-and-hold captcha
def detect_press_and_hold_captcha(driver):
    """Detect press-and-hold captcha"""
    return safe_run(lambda: bool(get_press_hold_context(driver)), False)

# Read progress percentage in the current frame
def get_progress_percent(driver):
    """Read progress percentage from captcha in the current frame"""
    return safe_run(lambda: driver.execute_script("""
        function firstGrowingBar() {
            const nodes = Array.from(document.querySelectorAll('div,span,p'));
            const bars = nodes.filter(n => {
                const style = (n.getAttribute('style') || '').toLowerCase();
                if (!/width:\\s*\\d+(?:\\.\\d+)?px/.test(style)) return false;
                const r = n.getBoundingClientRect();
                return r.width >= 1 && r.height >= 4 && r.height <= 40;
            });
            return bars[0] || null;
        }

        function findTrack(el) {
            if (!el) return null;
            const bw = el.getBoundingClientRect().width;
            let node = el.parentElement;
            for (let hop = 0; node && hop < 6; hop++, node = node.parentElement) {
                const cs = getComputedStyle(node);
                const r = node.getBoundingClientRect();
                const isTrackish =
                    r.width > bw + 4 &&
                    r.width >= 40 &&
                    (cs.overflowX === 'hidden' || cs.overflow === 'hidden' || cs.overflow === 'clip');
                if (isTrackish) return node;
            }
            return null;
        }

        const bar = firstGrowingBar();
        if (!bar) return null;
        const track = findTrack(bar);
        if (!track) return null;

        const bw = bar.getBoundingClientRect().width;
        const tw = track.getBoundingClientRect().width;
        if (tw <= 0) return null;

        return Math.max(0, Math.min(100, (bw / tw) * 100));
    """), None)

# Read progress percentage from any frame (searches all iframes)
from outlook_backend_python.helpers.browser import find_frame_with
def get_progress_percent_any_frame(driver):
    """
    Search all frames for the captcha progress bar and return its percent.
    Returns None if not found.
    """
    selectors = [
        'div[style*="width"]',
        'span[style*="width"]',
        'div[role="progressbar"]',
        'div[aria-valuenow]',
        'div[class*="progress" i]',
        'span[class*="progress" i]'
    ]
    # Try main frame and all iframes
    orig_handle = driver.current_window_handle
    try:
        res = find_frame_with(driver, selectors)
        if res['frame']:
            # Switch to the frame containing the progress bar
            frame = res['frame']
            # Selenium's driver.switch_to is already in the correct frame if res['frame'] is driver
            pct = get_progress_percent(frame)
            # Always switch back to default content after reading
            driver.switch_to.default_content()
            return pct
        else:
            driver.switch_to.default_content()
            return None
    except Exception:
        driver.switch_to.default_content()
        return None

# Handle press-and-hold captcha
def handle_press_and_hold_captcha(driver, max_attempts=3):
    """Handle press-and-hold captcha"""
    MIN_HOLD_MS = 6500   # backup if we fail to read percent
    MAX_HOLD_MS = 14000  # slightly higher to tolerate slower bars

    for attempt in range(1, max_attempts + 1):
        print(f"Press & hold challenge detected... (attempt {attempt}/{max_attempts})")

        ctx = get_press_hold_context(driver)
        if not ctx:
            print("Could not locate challenge UI.")
            return False
            
        click_point = ctx.get('click_point')
        if not click_point:
            print("No click point available.")
            return False

        # Move to the exact point and hold
        pyautogui.moveTo(click_point['x'], click_point['y'], duration=0.5)
        human_pause(150, 40)
        print("Holding mouse (monitoring progress %)…")
        pyautogui.mouseDown()

        best = 0
        stagnant_count = 0
        last_pct = -1

        NEAR_DONE = 99
        STALL_READS = 14       # ~1.4s no change at 100ms interval
        STABLE_DONE_READS = 8  # ~0.8s stably near 100%

        t0 = time.time() * 1000  # milliseconds
        while True:
            # If widget vanished, stop holding
            gone = not detect_press_and_hold_captcha(driver)
            if gone:
                print("Challenge disappeared while holding - releasing")
                break

        # Prefer proper %; otherwise use time fallback
        pct = get_progress_percent_any_frame(driver)
        if pct is not None:
            delta = abs(pct - last_pct) if last_pct != -1 else 0
            stagnant_count = delta < 0.25 if last_pct != -1 else 0
            last_pct = pct
            best = max(best, pct)

            if pct >= NEAR_DONE and stagnant_count >= STABLE_DONE_READS:
                print(f"Near 100% and stable ({pct:.1f}%) - releasing")
                break
            if pct >= 95 and stagnant_count >= STALL_READS:
                print(f"High & stagnant ({pct:.1f}%) - releasing")
                break

            print(f"Progress: {pct:.1f}% (best {best:.1f}%)")
        else:
            held = time.time() * 1000 - t0
            if held >= MIN_HOLD_MS:
                print("No progress metric; min time reached - releasing")
                break

            held = time.time() * 1000 - t0
            if held >= MAX_HOLD_MS:
                print("Max hold reached - releasing")
                break

            sleep(100)

        pyautogui.mouseUp()
        held_ms = time.time() * 1000 - t0
        print(f"Released after {held_ms:.0f} ms.")

        # Let UI finish
        sleep(1800)

        # Completed if challenge disappears
        still_there = detect_press_and_hold_captcha(driver)
        if not still_there:
            print("Challenge completed successfully.")
            return True

        # Check explicit retry text
        need_retry = safe_run(lambda: driver.execute_script("""
            const el = document.querySelector('[role="alert"], p[role="alert"]');
            const t = el ? (el.textContent || '').toLowerCase() : '';
            return t.includes('please try again') || t.includes('try again');
        """), False)

        if need_retry:
            print("Challenge says retry; pausing briefly…")
            sleep(900)
            continue

        print("Challenge still visible after release; retrying…")
        sleep(900)

    print("All press & hold attempts exhausted.")
    return False

# Wait for and solve press-and-hold challenge
def wait_for_and_solve_press_hold(driver, appear_timeout_ms=25000, max_attempts=3):
    """Wait for press-and-hold challenge to appear and solve it"""
    t0 = time.time() * 1000
    while time.time() * 1000 - t0 < appear_timeout_ms:
        seen = detect_press_and_hold_captcha(driver)
        if seen:
            ok = handle_press_and_hold_captcha(driver, max_attempts)
            return ok
        sleep(300)
    return False

__all__ = [
    'detect_press_and_hold_captcha',
    'handle_press_and_hold_captcha',
    'wait_for_and_solve_press_hold',
    'get_progress_percent_any_frame'
]
