# ============================================================================
# TEMPORARILY DISABLED: This module is not currently used
# ============================================================================
# Currently using only Ollama for text analysis.
# LangDetect functionality might be re-enabled in future versions.
# The code is kept for reference and potential future use.
# ============================================================================

from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

class DetectionSlovak:

    @staticmethod
    def is_slovak(text: str) -> bool:

        try:
            cleaned_text = text.replace('\n', ' ').strip()
            detected_lang = detect(cleaned_text)
            return detected_lang == 'sk'

        except LangDetectException:
            return False
