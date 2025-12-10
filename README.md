#  🎭 Automated WEB Extracted Text Classification <br> & Captcha Solver 

An automated web scraping and text classification tool using Selenium, BeautifulSoup4, Ollama AI, and PyPasser for captcha solving.

## 📑 Description

This project automates the process of logging into a website, solving reCAPTCHA v2 challenges, extracting text from web pages, and classifying that text using a local AI model (Ollama with gpt-oss). Based on the AI's classification, the bot automatically clicks appropriate buttons (Yes/No) to approve or reject content according to predefined criteria.

## 📍 Key Features

- **Automated Login** - Email-based authentication with anti-detection measures
- **reCAPTCHA v2 Solver** - Automatic captcha solving using PyPasser with manual fallback
- **Text Extraction** - Web scraping using BeautifulSoup4 with CSS selectors
- **AI-Powered Classification** - Local LLM analysis via Ollama (gpt-oss model)
- **Auto-Restart** - Recovers from errors automatically with configurable retry limits
- **Progress Tracking** - Saves progress to resume from interruptions
- **Anti-Detection** - Browser fingerprint masking to avoid bot detection

## 🛠️ Tech Stack

- **Selenium** - Browser automation and button clicking
- **BeautifulSoup4** - HTML parsing and text extraction
- **Ollama** - Local LLM for text analysis (gpt-oss model)
- **PyPasser** - Automated reCAPTCHA v2 solving
- **Python 3.13** - Core programming language

## 📥 Installation

### Prerequisites

1. **Python 3.13+** installed
2. **Chrome/Chromium browser** installed
3. **Ollama** installed and running locally

### Quick Start Guide

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

## ⚙️ Configuration

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

## 🦠 Troubleshooting

### Testing with try.py Demo

If `test_solve/try.py` fails:

**Error: ChromeDriver not found**
```bash
# Install webdriver-manager
pip install webdriver-manager
```

**Error: Chrome binary not found**
- Update Chrome/Chromium to latest version
- Or specify path in try.py:
```python
options.binary_location = "/path/to/chrome"
```

**Captcha solving fails in demo**
- This is normal - PyPasser success rate is 70-90%
- Try running the demo multiple times
- If it consistently fails, manual solving will be used in main program

### Ollama Connection Error
```
Failed to connect to Ollama at http://localhost:11434
```
**Solution:** Start Ollama service
```bash
ollama serve
```

### Browser Not Found
```
selenium.common.exceptions.WebDriverException
```
**Solution:** Update `BROWSER_BINARY_PATH` in `config.py` to correct Chrome/Chromium location

### Captcha Not Solving
```
pypasser failed, trying manual...
```
**Solution:** 
- Normal behavior, solve manually in browser
- PyPasser success rate varies (70-90%)
- Manual solving always available as fallback

### Button Not Found
```
Button not found - page state corrupted
```
**Solution:** Check CSS selectors in `config.py`:
- `BUTTON_YES_SELECTOR`
- `BUTTON_NO_SELECTOR`
- Use browser DevTools to verify correct selectors

### Question Not Changing
```
Question did not change - page stuck
```
**Solution:**
- Increase `NEW_QUESTION_TIMEOUT` in config
- Check if captcha appeared (may need solving)
- Verify page actually loads new content

## ⚠️ Important Notes

### First Time Setup

**Always test captcha solving first!** Run `python test_solve/try.py` before attempting the main program. This will:
- Verify your Chrome/Chromium installation
- Test PyPasser functionality  
- Confirm anti-detection settings work
- Save you time troubleshooting later

If the demo fails multiple times, you may need to rely on manual captcha solving in the main program.

### Anti-Detection Measures
The browser is configured with anti-detection to avoid bot detection:
- Removes `navigator.webdriver` property
- Disables automation flags
- Uses custom window size
- May still be detected by advanced systems

### Captcha Solving
- **Automatic solving** takes 30-120 seconds
- **Success rate** varies (70-90%)
- **Manual fallback** always available (3 min timeout)
- PyPasser uses audio challenge solving

### Rate Limiting
- No built-in rate limiting
- Add delays in config if needed:
```python
time.sleep(random.uniform(1, 3))  # Add to code
```

## ⚖️ Legal Disclaimer

This tool is for **educational purposes only**. Users are responsible for:
- Complying with website Terms of Service
- Respecting robots.txt and rate limits
- Obtaining necessary permissions
- Following local laws and regulations

The authors assume no liability for misuse.

## 🔗 Useful Links

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [PyPasser GitHub](https://github.com/xHossein/PyPasser)
- [reCAPTCHA Documentation](https://developers.google.com/recaptcha)
---
