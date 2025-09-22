# Browser configuration and frame helpers
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from outlook_backend_python.utils.helpers import safe_run, human_pause, sleep

# Human-like browser configuration
def configure_human_like_browser(driver):
    """Configure browser for human-like behavior"""
    # Set viewport size
    driver.set_window_size(1920, 1080)
    
    # Set extra HTTP headers
    driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
        'headers': {
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
    })
    
    # Execute JavaScript to modify browser properties
    driver.execute_script("""
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [
            { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
            { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
            { name: 'Native Client', filename: 'internal-nacl-plugin' }
        ]});
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        Object.defineProperty(navigator, 'permissions', { get: () => ({ query: async () => ({ state: 'granted' }) }) });
        if (!window.chrome) window.chrome = {};
        if (!window.chrome.runtime) window.chrome.runtime = {};
    """)

# Frame helpers
def find_frame_with(driver, selectors):
    """Find frame containing any of the given selectors"""
    try:
        # First check main frame
        for selector in selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return {'frame': driver, 'selector': selector}
            except (NoSuchElementException, Exception):
                continue
        
        # Check iframes
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        for iframe in iframes:
            try:
                driver.switch_to.frame(iframe)
                for selector in selectors:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                        if element.is_displayed():
                            return {'frame': driver, 'selector': selector}
                    except (NoSuchElementException, Exception):
                        continue
            except Exception:
                continue
            finally:
                driver.switch_to.default_content()
                
    except Exception:
        pass
    
    return {'frame': None, 'selector': None}

def frame_has_visible(frame, selector):
    """Check if frame has visible element matching selector"""
    try:
        if isinstance(frame, str):
            # If frame is a selector string, find the frame first
            frame_element = frame.find_element(By.CSS_SELECTOR, selector)
            return frame_element.is_displayed()
        else:
            element = frame.find_element(By.CSS_SELECTOR, selector)
            return element.is_displayed()
    except (NoSuchElementException, Exception):
        return False

def wait_in_any_frame(driver, selectors, timeout=15000):
    """Wait for element to appear in any frame"""
    from time import time
    t0 = time()
    
    while (time() - t0) * 1000 < timeout:
        res = find_frame_with(driver, selectors)
        if res['frame']:
            return res
        sleep(40)
    
    raise TimeoutException(f"Timed out waiting (any frame visible) for: {', '.join(selectors)}")

def click_next_in_frame(frame):
    """Click next/submit button in frame"""
    candidates = ['button[type="submit"]', 'input[type="submit"]', 'button#idSIButton9']
    
    from time import time
    t0 = time()
    timeout = 8000
    
    while (time() - t0) * 1000 < timeout:
        for sel in candidates:
            try:
                element = frame.find_element(By.CSS_SELECTOR, sel)
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    human_pause()
                    return True
            except (NoSuchElementException, Exception):
                continue
        
        sleep(120)
    
    # Fallback: press Enter
    try:
        body = frame.find_element(By.TAG_NAME, 'body')
        body.send_keys('\n')
        human_pause()
        return True
    except Exception:
        return False

__all__ = [
    'configure_human_like_browser',
    'find_frame_with',
    'frame_has_visible',
    'wait_in_any_frame',
    'click_next_in_frame'
]
