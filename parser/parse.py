from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from .trash_detector import DetectionSlovak
from .capcha_solver import CapchaSolver
from ollama.ollama import OllamaTextAnalyzer

# Класс для создания пользователя для дальнейшего использования
class UserLogin:

    # Установка драйвера браузера для парсинга
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.solve_captcha = CapchaSolver()

    # Создания всех полей для заполнения для захода а так же передача url перехода
    def user_login(self, url: str, email: str, email_locator: str):

        self.driver.get(url)
        time.sleep(2)

        # Заполняем email
        email_field = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, email_locator))
        )
        email_field.clear()
        email_field.send_keys(email)

        # Проверяем наличие капчи
        if self.solve_captcha.has_recaptcha(self.driver, verbose=True):
            if not self.solve_captcha.if_captcha(self.driver):
                print("[✗] Failed to solve captcha during login")
                return False

        # Кликаем кнопку отправки
        try:
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
        except:
            # Если не нашли по type, ищем любую кнопку
            submit_button = self.driver.find_element(By.TAG_NAME, 'button')
            submit_button.click()

        time.sleep(3)
        return True


# Основной класс парсинга страницы
class NewPageAnswer(UserLogin):

    def __init__(self, driver, selected_element: str):
        super().__init__(driver)
        self.last_question = None
        self.selected_element = selected_element

        self.analyzer = OllamaTextAnalyzer(
            model_name="gpt-oss",
            system_prompt = None
        )

    # Основная функция для выбора нужного нам текста со страницы
    def parse_text(self, selected_element: str = None) -> str|None:
        if selected_element is None:
            selected_element = self.selected_element

        try:
            html = self.driver.page_source
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                element = soup.select_one(selected_element)
                if element:
                    question = element.get_text().strip()
                    return question
                else:
                    print(f"[✗] No text found for selector: {selected_element}")
                    return None
            else:
                print("[✗] Can't find - html content")
                return None
        except Exception as e:
            print(f"[✗] Error parsing text: {e}")
            return None

    # Выбор нового вопроса
    def get_new_question(self, old_question: str, timeout=10) -> bool:

        start_time = time.time()

        while time.time() - start_time < timeout:

            new_question = self.parse_text()
            if new_question and new_question != old_question:
                print("[✓] New question found")
                return True
            time.sleep(0.5)

        print("[✗] No new question found ----- timeout")
        return False

    # Функция нажатия на кнопку ответа | которая будет его принимать от LLM которую мы укажем позже
    def click_answer(self, current_question: str, btn_no_locator: str, btn_yes_locator: str) -> bool:

        try:
            print(f"[DEBUG] Starting to process answer to question...")
            print(f"[DEBUG] Selectors: YES='{btn_yes_locator}', NO='{btn_no_locator}'")

            # Analyze question with Ollama
            try:
                is_good = self.analyzer.analyze(current_question)
                print(f"[✓] Ollama analysis result: {is_good}")
            except (ConnectionError, TimeoutError, ValueError) as e:
                print(f"[✗] Ollama analysis failed: {e}")
                # If Ollama fails, fall back to language detection only
                is_good = True

            # Determine which button to click
            if DetectionSlovak.is_slovak(current_question) and is_good:
                print('[✓] Correct text go to proceed')
                print(f"[DEBUG] Searching for YES button: {btn_yes_locator}")
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, btn_yes_locator)
                    print(f"[DEBUG] YES button found")
                except Exception as e:
                    print(f"[✗] YES button not found: {e}")
                    # Try to find all buttons
                    all_buttons = self.driver.find_elements(By.TAG_NAME, 'button')
                    print(f"[DEBUG] Total buttons on page: {len(all_buttons)}")
                    return False
            else:
                print('[✗] Incorrect text -------- trash')
                print(f"[DEBUG] Searching for NO button: {btn_no_locator}")
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, btn_no_locator)
                    print(f"[DEBUG] NO button found")
                except Exception as e:
                    print(f"[✗] NO button not found: {e}")
                    # Try to find all buttons
                    all_buttons = self.driver.find_elements(By.TAG_NAME, 'button')
                    print(f"[DEBUG] Total buttons on page: {len(all_buttons)}")
                    return False

            print("[DEBUG] Trying to click button...")
            button.click()
            print("[DEBUG] Button clicked successfully, waiting for load...")
            time.sleep(3)

            # Check for captcha after click
            if self.solve_captcha.has_recaptcha(self.driver, verbose=True):
                print("[!] Captcha appeared after click, solving...")
                if not self.solve_captcha.if_captcha(self.driver):
                    print("[✗] Failed to solve captcha after click")
                    return False

                print("[✓] Captcha solved, waiting for page to update...")
                time.sleep(3)
            else:
                print("[✓] No captcha detected after click")

            # Check if question changed (give more time)
            print("[DEBUG] Checking if question changed...")
            if not self.get_new_question(current_question, timeout=15):
                print("[✗] Question not changed after 15 seconds")

                # Perhaps question already changed during captcha solving
                new_q = self.parse_text()
                if new_q and new_q != current_question:
                    print("[✓] Question already changed during captcha solving")
                    return True
                else:
                    print("[✗] Question really didn't change")
                    return False

            return True

        except Exception as e:
            print(f"[✗] Error clicking answer: {e}")
            return False