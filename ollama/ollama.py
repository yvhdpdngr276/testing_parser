import requests
import json
from typing import Optional


class OllamaTextAnalyzer:
   
    def __init__(
            self,
            model_name: str = "gpt-oss",
            ollama_url: str = "http://localhost:11434",
            system_prompt: str = None
    ):
   
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.api_endpoint = f"{ollama_url}/api/generate"

     
        if system_prompt is None:
            self.system_prompt = """analyze text"""
        else:
            self.system_prompt = system_prompt

    def analyze(self, text: str, timeout: int = 30) -> bool:
     

        full_prompt = f"{self.system_prompt}\n\nText to analyze:\n{text}\n\nAnswer (true/false):"

     
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1, 
                "top_p": 0.9
            }
        }

        try:
           
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()

            result = response.json()
            model_response = result.get("response", "").strip().lower()

          
            print(f"[DEBUG] Ollama raw response: '{model_response}'")

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

      
        if "true" in response or "yes" in response or "ano" in response:
            return True
        elif "false" in response or "no" in response or "nie" in response:
            return False
        else:
            raise ValueError(
                f"Model answer not correct: '{response}'. "
                "Expected 'yes'/'no' or 'ano'/'nie'."
            )

