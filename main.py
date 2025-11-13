from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from parser.parse import NewPageAnswer
import time

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  AUTOMATIC QUESTION PARSER")
    print("="*60)
    print("ℹ  Captcha will be solved automatically via pypasser")
    print("ℹ  If it fails - you can solve it manually")
    print("="*60 + "\n")

    # Настройка Chrome опций
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')

    # Создаем драйвер
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Удаляем webdriver свойство для обхода детекта
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        # Создаем объект с указанием селектора элемента с вопросом
        parser = NewPageAnswer(driver, '#veta-text')

        # Логинимся
        print("\n=== Starting login ===")
        if parser.user_login(
            'example.com',
            'email@gamil.com',
            '#email'
        ):
            print("[✓] Login successful\n")
        else:
            print("[✗] Login failed")
            driver.quit()
            exit(1)

        # Check for captcha on main page after login
        print("[*] Checking for captcha on main page...")
        if parser.solve_captcha.has_recaptcha(driver, verbose=True):
            print("[!] Captcha detected after login, solving...")
            if not parser.solve_captcha.if_captcha(driver):
                print("[✗] Failed to solve captcha on main page")
                driver.quit()
                exit(1)
            print("[✓] Captcha on main page solved!")

            # Wait for page to load after captcha solving
            time.sleep(3)
        else:
            print("[✓] No captcha detected on main page")

        # Основной цикл обработки вопросов
        for i in range(25):
            print(f"\n{'='*50}")
            print(f"Question {i+1}/10")
            print('='*50)

            # Получаем текущий вопрос
            current_question = parser.parse_text()

            if not current_question:
                print("[✗] Failed to get question")
                break

            print(f"Question: {current_question[:100]}...")

            # Отвечаем на вопрос
            if parser.click_answer(
                current_question,
                '#btn-nepouzitelna',
                '#btn-pouzitelna'
            ):
                print(f"[✓] Question {i+1} answered successfully")
            else:
                print(f"[✗] Failed to answer question {i+1}")
                # DON'T STOP, keep trying
                print("[*] Attempting to continue...")

        print("\n" + "="*50)
        print("[✓] Program finished!")
        print("="*50)

    except Exception as e:
        print(f"\n[✗] Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress Enter to close browser...")
        driver.quit()