from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Patch pypasser to use JavaScript click instead of regular click
def patched_click_check_box(driver):
    """Patched checkbox click using JavaScript"""
    WebDriverWait(driver, 20).until(
        EC.frame_to_be_available_and_switch_to_it(
            (By.XPATH, "//iframe[contains(@src, 'recaptcha/api2/anchor')]")
        )
    )
    check_box = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
    )
    driver.execute_script("arguments[0].click();", check_box)
    driver.switch_to.default_content()

# Import and patch pypasser
from pypasser import reCaptchaV2
import pypasser.reCaptchaV2 as recaptcha_module

try:
    recaptcha_module.reCaptchaV2._reCaptchaV2__click_check_box__ = staticmethod(patched_click_check_box)
    print("[INFO] pypasser patched successfully")
except AttributeError:
    try:
        setattr(recaptcha_module.reCaptchaV2, '_reCaptchaV2__click_check_box__', staticmethod(patched_click_check_box))
        print("[INFO] pypasser patched (method 2)")
    except:
        print("[WARNING] Failed to patch pypasser, may not work")


class CapchaSolver:
    """Handles reCaptcha detection and solving"""

    def save_screenshot(self, driver, name="debug"):
        """Save screenshot for debugging"""
        try:
            filename = f"{name}_{int(time.time())}.png"
            driver.save_screenshot(filename)
        except Exception as e:
            pass

    def has_recaptcha(self, driver, verbose=False) -> bool:
        """Check if reCaptcha is present on the page"""
        try:
            # Check recaptcha container
            try:
                recaptcha_container = driver.find_element(By.ID, 'recaptcha-container')
                is_displayed = recaptcha_container.is_displayed()

                if not is_displayed:
                    return False

                if is_displayed:
                    iframes = driver.find_elements(By.CSS_SELECTOR, 'iframe[src*="recaptcha/api2/anchor"]')
                    return len(iframes) > 0
            except:
                pass

            # Check visible anchor iframes
            iframes = driver.find_elements(By.CSS_SELECTOR, 'iframe[src*="recaptcha/api2/anchor"]')
            visible_iframes = [iframe for iframe in iframes if iframe.is_displayed()]
            if len(visible_iframes) > 0:
                return True

            # Check g-recaptcha elements
            elements = driver.find_elements(By.CSS_SELECTOR, '#g-recaptcha, .g-recaptcha')
            visible_elements = [el for el in elements if el.is_displayed()]
            if len(visible_elements) > 0:
                return True

            return False

        except Exception as e:
            if verbose:
                print(f"[!] Error checking captcha: {e}")
            return False

    def solve_captcha_manual_wait(self, driver, timeout=None) -> bool:
        """Wait for user to solve captcha manually"""
        if timeout is None:
            timeout = config.CAPTCHA_MANUAL_TIMEOUT

        print("\n" + "="*70)
        print("  MANUAL CAPTCHA SOLVING REQUIRED")
        print("="*70)
        print("  Please solve the captcha in the browser.")
        print(f"  You have {timeout//60} minute(s) and {timeout%60} seconds.")
        print("  The program will continue automatically.")
        print("="*70 + "\n")

        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(2)

            if not self.has_recaptcha(driver):
                print("\n Captcha solved manually!")
                print("Searching for 'Continue' button...")
                try:
                    time.sleep(1)

                    buttons = driver.find_elements(By.TAG_NAME, 'button')
                    continue_button = None
                    for btn in buttons:
                        btn_text = btn.text.lower()
                        if 'pokračovať' in btn_text or 'продолжить' in btn_text or 'continue' in btn_text:
                            continue_button = btn
                            break

                    if not continue_button:
                        try:
                            form = driver.find_element(By.CSS_SELECTOR, 'form[action*="recaptcha"]')
                            continue_button = form.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                        except:
                            pass

                    if continue_button:
                        continue_button.click()
                        time.sleep(1)
                        return True
                    else:
                        return True

                except Exception as e:
                    print(f"[!] Error clicking button: {e}, but captcha solved")
                    return True

            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            print(f"\r Waiting... Time left: {remaining} sec", end="", flush=True)

        print("\n Timeout expired")
        return False

    def solve_captcha_auto(self, driver) -> bool:
        """Automatically solve captcha using pypasser"""
        print("Starting AUTOMATIC captcha solving...")
        print("WARNING: May take 30-120 seconds...")

        try:
            print("Running pypasser...")
            start_time = time.time()
            is_solved = reCaptchaV2(driver=driver, play=False)
            elapsed = time.time() - start_time
            print(f"pypasser execution time: {elapsed:.2f}s")

            if is_solved:
                print("Captcha solved by pypasser!")
                time.sleep(1)
                return True
            else:
                print("pypasser failed, trying manual...")
                return self.solve_captcha_manual_wait(driver)

        except KeyboardInterrupt:
            print("\n Captcha solving interrupted by user (Ctrl+C)")
            return False
        except Exception as e:
            print(f"pypasser error: {type(e).__name__}: {e}")
            print("Switching to manual solving...")
            return self.solve_captcha_manual_wait(driver)

    def if_captcha(self, driver) -> bool:
        """Check and solve captcha if present"""
        if self.has_recaptcha(driver):
            print("Captcha detected")

            if self.solve_captcha_auto(driver):
                print("Captcha solved!")

                # Check if already gone
                if not self.has_recaptcha(driver, verbose=False):
                    print("Captcha completely resolved")
                    return True

                # Need to click Continue button
                print("Searching for 'Continue' button...")
                try:
                    time.sleep(1)

                    buttons = driver.find_elements(By.TAG_NAME, 'button')
                    continue_button = None
                    for btn in buttons:
                        if 'pokračovať' in btn.text.lower():
                            continue_button = btn
                            break

                    if not continue_button:
                        try:
                            form = driver.find_element(By.CSS_SELECTOR, 'form[action*="recaptcha"]')
                            continue_button = form.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                        except:
                            pass

                    if continue_button:
                        continue_button.click()
                        time.sleep(1)

                        # Verify captcha is gone
                        if self.has_recaptcha(driver, verbose=False):
                            raise RuntimeError("Captcha still present after solving")

                        print("Captcha verified gone")
                        return True
                    else:
                        raise RuntimeError("'Continue' button not found")

                except RuntimeError:
                    raise
                except Exception as e:
                    print(f"Error clicking 'Continue': {e}")
                    import traceback
                    traceback.print_exc()
                    raise RuntimeError(f"Error during 'Continue' button handling: {e}")
            else:
                print(" Failed to solve captcha")
                raise RuntimeError("Failed to solve captcha")

        print("No captcha detected")
        return True
