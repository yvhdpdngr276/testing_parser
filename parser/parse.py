from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import sys
import os
from .capcha_solver import CapchaSolver
from ollama.ollama import OllamaTextAnalyzer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class UserLogin:
    """Base class for user authentication"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.WEBDRIVER_WAIT_TIMEOUT)
        self.solve_captcha = CapchaSolver()

    def user_login(self, url: str, email: str, email_locator: str):
        """Perform login with email authentication"""
        self.driver.get(url)
        time.sleep(1)

        email_field = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, email_locator))
        )
        email_field.clear()
        email_field.send_keys(email)

        if self.solve_captcha.has_recaptcha(self.driver, verbose=True):
            self.solve_captcha.if_captcha(self.driver)

        try:
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
        except:
            submit_button = self.driver.find_element(By.TAG_NAME, 'button')
            submit_button.click()

        time.sleep(1)
        return True


class NewPageAnswer(UserLogin):
    """Main class for parsing and answering questions"""

    def __init__(self, driver, selected_element: str):
        super().__init__(driver)
        self.last_question = None
        self.selected_element = selected_element
        self.analyzer = OllamaTextAnalyzer(
            model_name=config.OLLAMA_MODEL_NAME,
            ollama_url=config.OLLAMA_URL,
            system_prompt=config.OLLAMA_SYSTEM_PROMPT
        )

    def parse_text(self, selected_element: str = None) -> str|None:
        """Extract text from page using BeautifulSoup"""
        if selected_element is None:
            selected_element = self.selected_element

        try:
            html = self.driver.page_source
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                element = soup.select_one(selected_element)
                if element:
                    return element.get_text().strip()
                else:
                    print(f"No text found for selector: {selected_element}")
                    return None
            else:
                print("Can't find html content")
                return None
        except Exception as e:
            print(f"Error parsing text: {e}")
            return None

    def get_new_question(self, old_question: str, timeout=None) -> bool:
        """Poll for new question with timeout"""
        if timeout is None:
            timeout = config.NEW_QUESTION_TIMEOUT

        start_time = time.time()
        while time.time() - start_time < timeout:
            new_question = self.parse_text()
            if new_question and new_question != old_question:
                print("New question found")
                return True
            time.sleep(config.POLLING_INTERVAL)

        print("No new question found - timeout")
        return False

    def click_answer(self, current_question: str, btn_no_locator: str, btn_yes_locator: str) -> bool:
        """Analyze question with Ollama and click appropriate button"""
        try:
            # Analyze with Ollama
            try:
                is_good = self.analyzer.analyze(current_question, timeout=config.OLLAMA_TIMEOUT)
                print(f"Ollama result: {is_good}")
            except (ConnectionError, TimeoutError, ValueError) as e:
                print(f"Ollama failed: {e}")
                raise RuntimeError(f"Ollama service unavailable: {e}")

            # Select button
            try:
                if is_good:
                    print('Text is good')
                    button = self.driver.find_element(By.CSS_SELECTOR, btn_yes_locator)
                else:
                    print('Text is trash')
                    button = self.driver.find_element(By.CSS_SELECTOR, btn_no_locator)
            except Exception as e:
                print(f"Button not found: {e}")
                raise RuntimeError(f"Button not found - page state corrupted: {e}")

            button.click()
            time.sleep(0.5)

            # Check for captcha
            if self.solve_captcha.has_recaptcha(self.driver, verbose=True):
                print("[!] Captcha appeared, solving...")
                self.solve_captcha.if_captcha(self.driver)
                print("Captcha solved")
                time.sleep(0.5)
            else:
                print("No captcha detected")

            # Wait for question change
            if not self.get_new_question(current_question):
                # Check if already changed during captcha
                new_q = self.parse_text()
                if new_q and new_q != current_question:
                    print("Question changed during captcha")
                    return True
                else:
                    raise RuntimeError("Question did not change - page stuck")

            return True

        except RuntimeError:
            raise
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Unexpected error during answer processing: {e}")
