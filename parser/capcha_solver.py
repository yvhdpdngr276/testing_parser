from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Патчим pypasser чтобы использовал JavaScript клик
def patched_click_check_box(driver):
    """Патченная версия клика на чекбокс с JS"""
    print("[DEBUG] Using patched pypasser version with JS click")

    WebDriverWait(driver, 20).until(
        EC.frame_to_be_available_and_switch_to_it(
            (By.XPATH, "//iframe[contains(@src, 'recaptcha/api2/anchor')]")
        )
    )

    check_box = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
    )

    # Используем JavaScript клик вместо обычного
    print("[DEBUG] Executing JavaScript click on checkbox...")
    driver.execute_script("arguments[0].click();", check_box)
    print("[DEBUG] JavaScript click executed")

    driver.switch_to.default_content()

# Импортируем и патчим pypasser
from pypasser import reCaptchaV2
import pypasser.reCaptchaV2 as recaptcha_module

# Патчим метод клика (name mangling в Python)
try:
    recaptcha_module.reCaptchaV2._reCaptchaV2__click_check_box__ = staticmethod(patched_click_check_box)
    print("[INFO] pypasser successfully patched for JavaScript click")
except AttributeError:
    # Если не получилось, пробуем другой способ
    try:
        # Патчим через setattr
        setattr(recaptcha_module.reCaptchaV2, '_reCaptchaV2__click_check_box__', staticmethod(patched_click_check_box))
        print("[INFO] pypasser successfully patched (method 2)")
    except:
        print("[WARNING] Failed to patch pypasser, may not work")

class CapchaSolver:

    def save_screenshot(self, driver, name="debug"):
        """Сохраняет скриншот для отладки"""
        try:
            filename = f"{name}_{int(time.time())}.png"
            driver.save_screenshot(filename)
            print(f"[DEBUG] Screenshot saved: {filename}")
        except Exception as e:
            print(f"[DEBUG] Failed to save screenshot: {e}")

    # Проверяет наличие капчи на странице
    def has_recaptcha(self, driver, verbose=False) -> bool:
        try:
            if verbose:
                print("[DEBUG] Checking for captcha...")

            # Проверяем контейнер капчи - он должен быть видимым
            try:
                recaptcha_container = driver.find_element(By.ID, 'recaptcha-container')
                is_displayed = recaptcha_container.is_displayed()
                if verbose:
                    print(f"[DEBUG] Captcha container found, visibility: {is_displayed}")

                # Если контейнер скрыт - капчи нет
                if not is_displayed:
                    if verbose:
                        print("[DEBUG] Captcha container hidden - no captcha")
                    return False

                # Если контейнер видимый - проверяем iframe внутри
                if is_displayed:
                    iframes = driver.find_elements(By.CSS_SELECTOR, 'iframe[src*="recaptcha/api2/anchor"]')
                    if verbose:
                        print(f"[DEBUG] Found visible anchor iframes: {len(iframes)}")
                    return len(iframes) > 0

            except:
                # Если контейнера нет - проверяем по старой логике
                if verbose:
                    print("[DEBUG] Captcha container not found, checking iframes")
                pass

            # Проверяем видимые iframe с recaptcha anchor
            iframes = driver.find_elements(By.CSS_SELECTOR, 'iframe[src*="recaptcha/api2/anchor"]')
            visible_iframes = [iframe for iframe in iframes if iframe.is_displayed()]

            if verbose:
                print(f"[DEBUG] Found anchor iframes: {len(iframes)}, visible: {len(visible_iframes)}")

            if len(visible_iframes) > 0:
                return True

            # Проверяем элементы g-recaptcha которые видимы
            elements = driver.find_elements(By.CSS_SELECTOR, '#g-recaptcha, .g-recaptcha')
            visible_elements = [el for el in elements if el.is_displayed()]

            if verbose:
                print(f"[DEBUG] Found g-recaptcha elements: {len(elements)}, visible: {len(visible_elements)}")

            if len(visible_elements) > 0:
                return True

            if verbose:
                print("[DEBUG] No visible captcha found")
            return False

        except Exception as e:
            if verbose:
                print(f"[DEBUG] Error checking captcha: {e}")
            return False


    def click_recaptcha_checkbox(self, driver) -> bool:
        """
        Кликает на чекбокс 'I'm not a robot'

        Returns:
            True если кликнули успешно
        """
        try:
            print("[*] Searching for reCAPTCHA iframe...")

            # Ждем появления страницы
            time.sleep(2)

            # Сохраняем скриншот для отладки
            self.save_screenshot(driver, "before_captcha_click")

            # Ищем все iframe на странице
            all_iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            print(f"[DEBUG] Total iframes found on page: {len(all_iframes)}")

            # Выводим информацию о всех iframe
            for i, iframe in enumerate(all_iframes):
                src = iframe.get_attribute('src')
                title = iframe.get_attribute('title')
                print(f"[DEBUG] iframe {i}: src='{src[:100] if src else 'None'}...', title='{title}'")

            # Ищем iframe с recaptcha
            recaptcha_iframes = driver.find_elements(By.CSS_SELECTOR, 'iframe[src*="recaptcha"]')
            print(f"[DEBUG] Found recaptcha iframes: {len(recaptcha_iframes)}")

            if len(recaptcha_iframes) == 0:
                print("[✗] No recaptcha iframe found")
                return False

            # Берем первый iframe с anchor (не challenge)
            target_iframe = None
            for iframe in recaptcha_iframes:
                src = iframe.get_attribute('src')
                if 'anchor' in src:
                    target_iframe = iframe
                    print(f"[DEBUG] Selected iframe: {src[:100]}...")
                    break

            if not target_iframe:
                target_iframe = recaptcha_iframes[0]
                print(f"[DEBUG] Using first iframe")

            print("[*] Switching to captcha iframe...")
            driver.switch_to.frame(target_iframe)

            # Даем время на загрузку содержимого iframe
            time.sleep(2)

            # Ищем чекбокс несколькими способами
            print("[*] Searching for checkbox...")

            checkbox = None
            try:
                # Способ 1: по ID
                checkbox = driver.find_element(By.ID, 'recaptcha-anchor')
                print("[DEBUG] Checkbox found by ID")
            except:
                try:
                    # Способ 2: по классу
                    checkbox = driver.find_element(By.CLASS_NAME, 'recaptcha-checkbox-border')
                    print("[DEBUG] Checkbox found by class")
                except:
                    try:
                        # Способ 3: по CSS селектору
                        checkbox = driver.find_element(By.CSS_SELECTOR, '.recaptcha-checkbox')
                        print("[DEBUG] Checkbox found by CSS selector")
                    except:
                        print("[✗] Failed to find checkbox")
                        driver.switch_to.default_content()
                        return False

            if checkbox:
                print("[*] Clicking 'I'm not a robot' checkbox...")

                try:
                    # Пробуем обычный клик
                    checkbox.click()
                    print("[DEBUG] Regular click executed")
                except:
                    print("[DEBUG] Regular click failed, using JavaScript")
                    # Если не получилось - используем JavaScript клик
                    driver.switch_to.default_content()
                    driver.switch_to.frame(target_iframe)
                    driver.execute_script("arguments[0].click();", checkbox)
                    print("[DEBUG] JavaScript click executed")

                time.sleep(3)

                # Возвращаемся в основной контент
                driver.switch_to.default_content()
                print("[✓] Click executed successfully")
                return True
            else:
                driver.switch_to.default_content()
                return False

        except Exception as e:
            print(f"[✗] Error clicking checkbox: {e}")
            import traceback
            traceback.print_exc()
            try:
                driver.switch_to.default_content()
            except:
                pass
            return False

    def solve_captcha_manual_wait(self, driver, timeout=120) -> bool:
        """
        Ждет пока пользователь решит капчу вручную

        Returns:
            True если капча решена
        """
        print("\n" + "="*70)
        print("  MANUAL CAPTCHA SOLVING REQUIRED")
        print("="*70)
        print("  Please solve the captcha in the browser.")
        print("  You have 2 minutes.")
        print("  The program will continue automatically after solving.")
        print("="*70 + "\n")

        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(2)

            # Проверяем исчезла ли капча
            if not self.has_recaptcha(driver):
                print("\n[✓] Captcha solved manually!")

                # После решения нужно нажать кнопку "Продолжить"
                print("[*] Searching for 'Continue' button...")
                try:
                    time.sleep(2)

                    # Ищем кнопку "Pokračovať"
                    buttons = driver.find_elements(By.TAG_NAME, 'button')
                    continue_button = None
                    for btn in buttons:
                        btn_text = btn.text.lower()
                        if 'pokračovať' in btn_text or 'продолжить' in btn_text or 'continue' in btn_text:
                            continue_button = btn
                            print(f"[DEBUG] Found button: {btn.text}")
                            break

                    # Если не нашли по тексту, ищем submit в форме
                    if not continue_button:
                        try:
                            form = driver.find_element(By.CSS_SELECTOR, 'form[action*="recaptcha"]')
                            continue_button = form.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                            print("[DEBUG] Found submit button in form")
                        except:
                            pass

                    if continue_button:
                        print("[*] Clicking 'Continue' button...")
                        continue_button.click()
                        print("[✓] Button clicked, waiting for page load...")
                        time.sleep(3)
                        return True
                    else:
                        print("[!] 'Continue' button not found, but captcha is solved")
                        return True

                except Exception as e:
                    print(f"[!] Error clicking button: {e}, but captcha is solved")
                    return True

            # Показываем таймер
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            print(f"\r[*] Waiting for captcha solution... Time left: {remaining} sec", end="", flush=True)

        print("\n[✗] Timeout expired")
        return False

    def solve_captcha_auto(self, driver) -> bool:
        """
        Автоматически решает капчу через pypasser

        Returns:
            True если капча решена, False если нет
        """
        print("[*] Starting AUTOMATIC captcha solving...")
        print("[*] WARNING: Solving may take 30-120 seconds...")

        try:
            # Используем pypasser для автоматического решения
            print("[*] Starting pypasser for captcha solving...")
            start_time = time.time()

            is_solved = reCaptchaV2(driver=driver, play=False)

            elapsed = time.time() - start_time
            print(f"[DEBUG] pypasser execution time: {elapsed:.2f} seconds")

            if is_solved:
                print("[✓] Captcha solved by pypasser!")
                time.sleep(2)
                return True
            else:
                print("[✗] pypasser returned False, trying manual...")
                return self.solve_captcha_manual_wait(driver)

        except KeyboardInterrupt:
            print("\n[!] Captcha solving interrupted by user (Ctrl+C)")
            return False
        except Exception as e:
            print(f"[✗] pypasser error: {type(e).__name__}: {e}")
            # Если pypasser упал - даем шанс решить вручную
            print("[*] pypasser failed, switching to manual solving...")
            return self.solve_captcha_manual_wait(driver)


    def if_captcha(self, driver) -> bool:
        """
        Проверяет и решает капчу если она есть

        Returns:
            True если капчи нет или она успешно решена
            False если капча есть но не решена
        """
        if self.has_recaptcha(driver):
            print("[!] Captcha detected on page")

            # Автоматически решаем капчу
            if self.solve_captcha_auto(driver):
                print("[✓] Captcha successfully solved!")

                # После решения капчи нужно нажать кнопку "Pokračovať"
                print("[*] Searching for 'Continue' button after captcha...")
                try:
                    # Ищем кнопку с текстом "Pokračovať" внутри формы капчи
                    time.sleep(2)

                    # Способ 1: Ищем по тексту кнопки
                    buttons = driver.find_elements(By.TAG_NAME, 'button')
                    continue_button = None
                    for btn in buttons:
                        if 'pokračovať' in btn.text.lower() or 'продолжить' in btn.text.lower():
                            continue_button = btn
                            print(f"[DEBUG] Found 'Continue' button: {btn.text}")
                            break

                    # Способ 2: Если не нашли, ищем submit внутри формы с recaptcha
                    if not continue_button:
                        try:
                            form = driver.find_element(By.CSS_SELECTOR, 'form[action*="recaptcha"]')
                            continue_button = form.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                            print("[DEBUG] Found submit button in captcha form")
                        except:
                            pass

                    if continue_button:
                        print("[*] Clicking 'Continue' button...")
                        continue_button.click()
                        print("[✓] Button clicked, waiting for page load...")
                        time.sleep(3)
                        return True
                    else:
                        print("[✗] 'Continue' button not found")
                        return False

                except Exception as e:
                    print(f"[✗] Error clicking 'Continue' button: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                print("[✗] Failed to solve captcha automatically")
                return False

        # Капчи нет - все ОК
        print("[✓] No captcha detected")
        return True