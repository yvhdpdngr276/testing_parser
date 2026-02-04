
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white) ![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-4B0082?style=for-the-badge&logo=python&logoColor=white) 
![PyPasser](https://img.shields.io/badge/PyPasser-0055FF?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) 


##  Automated WEB Extracted Text Classification <br> & Captcha Solver 

- **Automated Login** - Email-based authentication with anti-detection measures
- **reCAPTCHA v2 Solver** - Automatic captcha solving using PyPasser with manual fallback
- **Text Extraction** - Web scraping using BeautifulSoup4 with CSS selectors
- **AI-Powered Classification** - Local LLM analysis via Ollama (gpt-oss model)
- **Auto-Restart** - Recovers from errors automatically with configurable retry limits
- **Progress Tracking** - Saves progress to resume from interruptions
- **Anti-Detection** - Browser fingerprint masking to avoid bot detection


## Installation

1. **Python 3.13+** installed
2. **Chrome/Chromium browser** installed
3. **Ollama** installed and running locally

**Step 1:** Install Ollama
```bash
# Linux/MacOS
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

**Step 2:** Pull the gpt-oss Model
```bash
ollama pull gpt-oss
```

**Step 3:** Install Python Dependencies

1. Clone the repository:
```bash
git clone https://github.com/yvhdpdngr276/testing_parser.git
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/MacOS
# or
.venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

**Step 4:** Test Captcha Solving (Recommended)

Before configuring and running the main program, test if captcha solving works:
```bash
python test_solve/try.py
```

This will open Google's reCAPTCHA demo page and attempt to solve it automatically. If you see "SUCCESS", you're ready to proceed!

**Step 5:** Configure the Project

Create your `config.py` file (see Configuration section below)

**Step 6:** Run the Main Program
```bash
python main.py
```

## Configuration 

Create a `config.py` file in the root directory with the following settings:
```python
# Browser Settings
BROWSER_BINARY_PATH = "/usr/bin/chromium"  # Path to Chrome/Chromium
BROWSER_WINDOW_SIZE = (1920, 1080)

# Login Credentials
LOGIN_URL = "https://example.com/login"
USER_EMAIL = "your-email@example.com"
EMAIL_SELECTOR = "input[type='email']"

# Page Selectors
QUESTION_TEXT_SELECTOR = ".question-text"  # CSS selector for text to classify
BUTTON_YES_SELECTOR = "button.approve"     # CSS selector for "Yes" button
BUTTON_NO_SELECTOR = "button.reject"       # CSS selector for "No" button

# Ollama Settings
OLLAMA_MODEL_NAME = "gpt-oss"
OLLAMA_URL = "http://localhost:11434"
OLLAMA_TIMEOUT = 30  # seconds

# System Prompt for Text Classification
OLLAMA_SYSTEM_PROMPT = """
Analyze the following text and determine if it meets quality standards.
Consider: grammar, relevance, coherence, and appropriateness.
Answer ONLY "true" (good text) or "false" (bad text).
Do not provide explanations.
"""

# Timing Settings
WEBDRIVER_WAIT_TIMEOUT = 10  # seconds
NEW_QUESTION_TIMEOUT = 15    # seconds to wait for new question
POLLING_INTERVAL = 0.5       # seconds between checks
CAPTCHA_WAIT_TIMEOUT = 10    # seconds
CAPTCHA_MANUAL_TIMEOUT = 180 # seconds for manual solving

# Task Settings
TOTAL_QUESTIONS = 100        # Number of questions to process
MAX_RESTARTS = 5             # Maximum restart attempts on errors

# Progress File
PROGRESS_FILE = "progress.json"
```



## ⚖️ Legal Disclaimer

This tool is for **educational purposes only**. Users are responsible for:
- Complying with website Terms of Service
- Respecting robots.txt and rate limits
- Obtaining necessary permissions
- Following local laws and regulations

The authors assume no liability for misuse.
