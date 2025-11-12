from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests
import re
import time
from pypasser import reCaptchaV2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


#Класс для создание пользователя для дальнейшего использования
class UserLogin:

    # Установка страницы браузера для парсинга
    def __init__(self,page):
        self.page = page

    #Проверяет наличие капчи на странице
    def _has_recaptcha(self) -> bool:

        try:
            if self.page.locator('iframe[src*="recaptcha"]').count() > 0:
                return True
            if self.page.locator('#g-recaptcha, .g-recaptcha').count() > 0:
                return True
            return False
        except Exception:
            return False

    def _solve_captcha_auto(self) -> str:
        """
        Автоматически решает капчу через Selenium + pypasser

        Returns:
            Токен капчи или пустую строку
        """
        print("[*] Запуск автоматического решения капчи...")

        current_url = self.page.url

        # Создаем Selenium driver для решения капчи
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get(current_url)
            time.sleep(2)

            # Автоматическое решение через pypasser
            print("[*] Решаем капчу автоматически (может занять 30-60 сек)...")
            is_solved = reCaptchaV2(driver=driver, play=False)

            if is_solved:
                print("[✓] Capcha solved automatically.!")

                # Получаем токен
                token = driver.execute_script(
                    "return document.querySelector('[name=\"g-recaptcha-response\"]').value"
                )
                return token
            else:
                print("[✗] Cant solve captcha.")
                return ""

        except Exception as e:
            print(f"[✗] Error with solving capcha: {e}")
            return ""
        finally:
            driver.quit()

    # Создания всех полей для заполнения для захода а так же передачя url перехода
    def user_login(self, url: str, email: str, email_locator: str):

        self.page.goto(url)
        self.page.locator(email_locator).fill(email)

        # Проверяем наличие капчи
        if self._has_recaptcha():
            print("[!] Find a captcha.")

            # Автоматически решаем капчу через Selenium
            captcha_token = self._solve_captcha_auto()

            if captcha_token:
                # Вставляем токен обратно в Playwright
                self.page.evaluate(f"""
                    () => {{
                        const element = document.querySelector('[name="g-recaptcha-response"]');
                        if (element) {{
                            element.value = '{captcha_token}';
                        }}
                    }}
                """)
                print("[✓] Token of capcha solved return")
            else:
                print("[✗] Cannot solve captcha automatically.")
                return False

        # Кликаем кнопку отправки
        self.page.get_by_role('button').click()
        self.page.wait_for_load_state('networkidle')
        return True

#Основной класс парсинга страницы
class NewPageAnswer(UserLogin):
    def __init__(self,page):
        super().__init__(page)
        self.last_question = None

    #Основная функция для выбора нужного нам текста со страницы
    def parse_text(self, selected_element: str) -> str|None:

        html = self.page.content()
        if html:
            soup = BeautifulSoup(html,'html.parser')
            element = soup.select_one(selected_element)
            if element:
                question = element.get_text().strip()
                return question
            else:
                print("No text found")
                return None
        else:
            print("Can't find - html content")
            return None

    # Выбор нового вопроса
    def get_new_question(self, old_question: str, timeout=10) -> bool:

        start_time = time.time()

        while time.time() - start_time < timeout:

            new_question = self.parse_text()
            if new_question and new_question != old_question:
                print("New question found")
                return True
            time.sleep(0.5)

        print("No new question found ----- timeout")
        return False

    # Функция нажатия на кнопку ответа | которая будет его принимать от LLM которую мы укажем позже
    def click_answer(self, answer: str, current_question: str, btn_no_locator: str, btn_yes_locator: str) -> bool:

        try:
            if answer == 'yes':
                print('Correct text go to proceed')
                self.page.locator(btn_yes_locator).click()
            else:
                print('Incorrect text -------- trash')
                self.page.locator(btn_no_locator).click()


            self.page.wait_for_load_state('networkidle')

            if not self.get_new_question(current_question):
                print("Question not changed")
                return False

            return True

        except Exception as e :
            print({e})
            return False

