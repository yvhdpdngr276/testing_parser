import requests
import json
from typing import Optional


class OllamaTextAnalyzer:
    """
    Класс для анализа текста с помощью модели Ollama (gpt-oss).
    Возвращает булево значение на основе системного промпта и входного текста.
    """
    def __init__(
            self,
            model_name: str = "gpt-oss",
            ollama_url: str = "http://localhost:11434",
            system_prompt: str = None
    ):
        """
        Инициализация анализатора.

        Args:
            model_name: Название модели в Ollama (по умолчанию "gpt-oss")
            ollama_url: URL для Ollama API (по умолчанию "http://localhost:11434")
            system_prompt: Системный промпт для модели
        """
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.api_endpoint = f"{ollama_url}/api/generate"

        # Системный промпт по умолчанию
        if system_prompt is None:
            self.system_prompt = """analyze text"""
        else:
            self.system_prompt = system_prompt

    def analyze(self, text: str, timeout: int = 30) -> bool:
        """
        Анализирует текст и возвращает булево значение.

        Args:
            text: Текст для анализа
            timeout: Таймаут запроса в секундах

        Returns:
            bool: True или False на основе анализа модели

        Raises:
            ConnectionError: Если не удается подключиться к Ollama
            ValueError: Если модель вернула некорректный ответ
        """
        # Формируем полный промпт
        full_prompt = f"{self.system_prompt}\n\nText to analyze:\n{text}\n\nAnswer (true/false):"

        # Подготовка запроса к Ollama
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Низкая температура для более детерминированных ответов
                "top_p": 0.9
            }
        }

        try:
            # Отправка запроса к Ollama
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()

            # Парсинг ответа
            result = response.json()
            model_response = result.get("response", "").strip().lower()

            # Извлечение булева значения
            return self.parse_boolean_response(model_response)

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Failed to connect to Ollama at {self.ollama_url}. "
                "Make sure Ollama is running."
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request exceeded timeout of {timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error requesting Ollama: {e}")

    def parse_boolean_response(self, response: str) -> bool:
        """
        Парсит ответ модели и извлекает булево значение.

        Args:
            response: Ответ модели

        Returns:
            bool: True или False

        Raises:
            ValueError: Если ответ не содержит четкого булева значения
        """
        response = response.strip().lower()

        # Проверка различных вариантов ответа
        if "true" in response or "nie" in response or "yes" in response:
            return True
        elif "false" in response or "ano" in response or "no" in response:
            return False
        else:
            raise ValueError(
                f"Model answer not correct: '{response}'. "
                "Expected 'true' or 'false'."
            )

    def set_system_prompt(self, new_prompt: str):
        """
        Обновляет системный промпт.

        Args:
            new_prompt: Новый системный промпт
        """
        self.system_prompt = new_prompt


# Пример использования
#if __name__ == "__main__":
#    # Создание анализатора с кастомным системным промптом
#    custom_prompt = """Ты - детектор спама. Анализируй текст и определи, является ли он спамом.
#Отвечай "true", если текст является спамом (реклама, мошенничество, навязчивые предложения).
#Отвечай "false", если текст не является спамом.
#Отвечай ТОЛЬКО "true" или "false", без дополнительных объяснений."""
#
#    analyzer = OllamaTextAnalyzer(
#        model_name="gpt-oss",
#        system_prompt=custom_prompt
#    )
#
#    # Тестовые тексты
#    test_texts = [
#        "Привет! Как дела?",
#        "СРОЧНО! Выиграй миллион! Переходи по ссылке СЕЙЧАС!!!",
#        "Встретимся завтра в 15:00 у кофейни?",
#        "Только сегодня! Скидка 90%! Купи сейчас!"
#    ]
#
#    print("Анализ текстов:\n")
#    for text in test_texts:
#        try:
#            is_spam = analyzer.analyze(text)
#            result = "СПАМ" if is_spam else "НЕ СПАМ"
#            print(f"Текст: {text[:50]}...")
#            print(f"Результат: {result} ({is_spam})\n")
#        except Exception as e:
#            print(f"Ошибка при анализе: {e}\n")