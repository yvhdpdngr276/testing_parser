from pypasser import reCaptchaV2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Working demonstration of capcha v2 solving in testing web case
def solve_captcha_demo():
    """Demo function showing how to solve captcha"""
    # Create an instance of webdriver with Chrome
    print("Setting up Chrome driver...")
    options = webdriver.ChromeOptions()

    # Anti-detection options
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Remove webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Open target
    driver.get('https://www.google.com/recaptcha/api2/demo')

    # Solve reCaptcha v2 via PyPasser
    is_checked = reCaptchaV2(driver=driver, play=False)

    if is_checked:
        # Click submit button
        driver.find_element(By.CSS_SELECTOR, '#recaptcha-demo-submit').click()
        if 'Verification Success' in driver.page_source:
            print('SUCCESS')
    else:
        print('FAIL')

    driver.quit()


if __name__ == '__main__':
    solve_captcha_demo()