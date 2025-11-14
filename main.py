from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from parser.parse import NewPageAnswer
import time
import sys
import json
import os
import config


def create_driver():
    """Creates Chrome WebDriver with anti-detection settings"""
    options = Options()
    options.binary_location = config.BROWSER_BINARY_PATH
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument(f'--window-size={config.BROWSER_WINDOW_SIZE[0]},{config.BROWSER_WINDOW_SIZE[1]}')

    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


# Progress tracking
def load_progress():
    """Load progress from JSON file, returns question number to start from"""
    if not os.path.exists(config.PROGRESS_FILE):
        return 0

    try:
        with open(config.PROGRESS_FILE, 'r') as f:
            data = json.load(f)
            completed = data.get('completed_questions', 0)
            if 0 <= completed < config.TOTAL_QUESTIONS:
                return completed
            else:
                print(f"[!] Invalid progress value {completed}, starting from 0")
                return 0
    except (json.JSONDecodeError, IOError) as e:
        print(f"[!] Error reading progress file: {e}")
        print("[!] Starting from question 1")
        return 0


def save_progress(question_num):
    """Save current progress to JSON file"""
    try:
        with open(config.PROGRESS_FILE, 'w') as f:
            json.dump({'completed_questions': question_num}, f)
    except IOError as e:
        print(f"[!] Warning: Could not save progress: {e}")


def clear_progress():
    """Remove progress file after successful completion"""
    try:
        if os.path.exists(config.PROGRESS_FILE):
            os.remove(config.PROGRESS_FILE)
            print("[*] Progress file cleared")
    except IOError as e:
        print(f"[!] Warning: Could not clear progress file: {e}")


def run_main_logic(restart_count=0):
    """Main program logic - login, solve questions, handle captcha"""
    driver = None

    try:
        driver = create_driver()

        if restart_count > 0:
            print(f"\n[!] === RESTART #{restart_count} ===\n")

        parser = NewPageAnswer(driver, config.QUESTION_TEXT_SELECTOR)

        print("=== Starting login ===")
        if parser.user_login(config.LOGIN_URL, config.USER_EMAIL, config.EMAIL_SELECTOR):
            print("[✓] Login successful\n")
        else:
            print("[✗] Login failed")
            raise RuntimeError("Login failed - restart required")

        # Check for captcha after login
        print("[*] Checking for captcha...")
        if parser.solve_captcha.has_recaptcha(driver, verbose=True):
            print("[!] Captcha detected, solving...")
            if not parser.solve_captcha.if_captcha(driver):
                raise RuntimeError("Failed to solve captcha - restart required")
            print("[✓] Captcha solved!")

            try:
                WebDriverWait(driver, config.CAPTCHA_WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, config.QUESTION_TEXT_SELECTOR))
                )
            except:
                time.sleep(1)
        else:
            print("[✓] No captcha detected")

        # Load progress
        start_from = load_progress()
        if start_from > 0:
            print(f"\n[*] Resuming from question {start_from + 1}/{config.TOTAL_QUESTIONS}")
            print(f"[*] {start_from} question(s) already completed")

        # Main question loop
        for i in range(start_from, config.TOTAL_QUESTIONS):
            print(f"\n{'='*50}")
            print(f"Question {i+1}/{config.TOTAL_QUESTIONS} (Restart #{restart_count})")
            print('='*50)

            current_question = parser.parse_text()
            if not current_question:
                raise RuntimeError(f"Failed to get question #{i+1} - restart required")

            print(f"Question: {current_question[:100]}...")

            if not parser.click_answer(current_question, config.BUTTON_NO_SELECTOR, config.BUTTON_YES_SELECTOR):
                raise RuntimeError(f"Failed to answer question #{i+1} - restart required")

            print(f"[✓] Question {i+1} answered successfully")
            save_progress(i + 1)

        print("\n" + "="*50)
        print(f"[✓] All {config.TOTAL_QUESTIONS} questions completed successfully!")
        print("="*50)
        clear_progress()

    except KeyboardInterrupt:
        print("\n[!] Program stopped by user (Ctrl+C)")
        raise
    except Exception as e:
        print(f"\n[✗] Critical error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        if driver:
            try:
                driver.quit()
                print("[*] Browser closed")
            except:
                pass


def main_with_restart():
    """Main function with automatic restart on critical errors"""
    print("\n" + "="*60)
    print("  AUTOMATIC QUESTION PARSER")
    print("="*60)
    print("ℹ  Captcha will be solved automatically via pypasser")
    print("ℹ  If it fails - you can solve it manually")
    print(f"ℹ  Auto-restart enabled (max {config.MAX_RESTARTS} attempts)")
    print("="*60 + "\n")

    restart_count = 0

    while restart_count <= config.MAX_RESTARTS:
        try:
            run_main_logic(restart_count)
            print("\n[✓] Program completed successfully!")
            break

        except KeyboardInterrupt:
            print("\n\n[!] Stopped by user")
            break

        except (RuntimeError, ConnectionError, TimeoutError) as e:
            restart_count += 1

            if restart_count > config.MAX_RESTARTS:
                print(f"\n[✗] Max restarts reached ({config.MAX_RESTARTS})")
                break

            print(f"\n{'='*60}")
            print(f"[!] CRITICAL ERROR: {e}")
            print(f"[!] Restarting immediately... (Attempt {restart_count}/{config.MAX_RESTARTS})")
            print(f"{'='*60}")

        except Exception as e:
            print(f"\n[✗] Unexpected error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            break

    input("\nPress Enter to exit...")
    sys.exit(0 if restart_count <= config.MAX_RESTARTS else 1)


if __name__ == "__main__":
    main_with_restart()