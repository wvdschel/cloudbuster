from random import random
from src.browser_helper import BrowserHelper

from botasaurus.browser import Driver
import cv2
import numpy as np
from time import sleep

CAPTURE_DEVICE_SCALING_JS = """
window.localStorage.setItem("device_pixel_ratio", window.devicePixelRatio);
"""

CAPTURE_CF_TOKEN_JS = """
var observer = new MutationObserver(function(mutations) {
  mutations.forEach(function(mutation) {
    if (mutation.type === "attributes") {
      console.log(`Updated attribute ${mutation.attributeName}: ${mutation.target.attributes[mutation.attributeName].value}`);
      if (mutation.attributeName === "value") {
        let newValue = mutation.target.attributes[mutation.attributeName].value;
        window.localStorage.setItem("captured_cf_token", newValue);
      }
    }
  });
});

observer.observe(document.querySelector("input[name=cf-turnstile-response]"), { attributes: true })
"""


def find_template_multiscale(large_image_path, template_path, 
                             scale_range=(0.5, 2.0), scale_steps=20):
    """
    Find template at different scales for better matching
    """
    large_img = cv2.imread(large_image_path)
    template = cv2.imread(template_path)
    
    if large_img is None or template is None:
        raise ValueError("Could not load images")
    
    best_match = None
    best_val = -1
    
    # Test different scales
    scales = np.linspace(scale_range[0], scale_range[1], scale_steps)
    
    for scale in scales:
        # Resize template
        resized_template = cv2.resize(template, None, fx=scale, fy=scale)
        
        # Skip if template is larger than image
        if (resized_template.shape[0] > large_img.shape[0] or 
            resized_template.shape[1] > large_img.shape[1]):
            continue
        
        # Perform template matching
        result = cv2.matchTemplate(large_img, resized_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Update best match if better
        if max_val > best_val:
            best_val = max_val
            h, w = resized_template.shape[:2]
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            best_match = (top_left, bottom_right, best_val, scale)
    
    return best_match


# @browser(proxy=os.getenv('PROXY') or None, output=os.getenv('OUTPUT_FILE') or 'output/scrape_cf_turnstile.json')
def scrape_cf_turnstile(link, proxy=None):
    with BrowserHelper(proxy) as driver:
        # Navigate to Cloudflare's Turnstile Captcha demo
        driver.get(link)

        retries = 20
        confidence = 0
        while True:
            driver.save_screenshot("cf_turnstile.png")
            top_left, bottom_right, confidence, _scale = find_template_multiscale("output/screenshots/cf_turnstile.png", "needle.png")
            print(f'confidence: {confidence}')
            if confidence > 0.42:
                break
            retries -= 1
            if retries == 0:
                print("failed to find turnstile")
                return driver.get_cookies_and_local_storage()
            sleep(0.5)

        driver.run_js(CAPTURE_DEVICE_SCALING_JS)
        scaling_factor = float(driver.get_local_storage()['device_pixel_ratio'])
        print(f"scaling factor: {scaling_factor}")

        x_offset = 0.6 * random() * (bottom_right[0] - top_left[0]) / scaling_factor
        y_offset = 0.5 * (bottom_right[1] - top_left[1]) / scaling_factor
        x_pos = top_left[0] / scaling_factor + x_offset
        y_pos = top_left[1] / scaling_factor + y_offset

        driver.run_js(CAPTURE_CF_TOKEN_JS)

        # # Enable human mode for realistic, human-like mouse movements
        driver.enable_human_mode()
        print(f"Clicking {x_pos},{y_pos}")
        driver.click_at_point(x_pos, y_pos)

        retries = 20
        while 'captured_cf_token' not in driver.get_local_storage():
            sleep(0.1)
            retries -= 1
            if retries == 0:
                print("failed to find CF token")
                return driver.get_cookies_and_local_storage()

        print(f"CF token: {driver.get_local_storage()['captured_cf_token']}")

        driver.disable_human_mode()

        return driver.get_cookies_and_local_storage()
