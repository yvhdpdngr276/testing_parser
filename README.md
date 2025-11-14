# 😊 Automated Text Classification & Captcha Solver

An automated web scraping and text classification tool using Selenium, BeautifulSoup4, Ollama AI, and PyPasser for captcha solving.

## 📋 Description

This project automates the process of logging into a website, solving reCAPTCHA v2 challenges, extracting text from web pages, and classifying that text using a local AI model (Ollama with gpt-oss). Based on the AI's classification, the bot automatically clicks appropriate buttons (Yes/No) to approve or reject content according to predefined criteria.

## 🎯 Key Features

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

## 📦 Installation

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
git clone <repository-url>
cd <project-folder>
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
python parser/try.py
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

## 🚀 Usage

### Testing Captcha Solving (Demo)

Before running the main program, you can test the captcha solving functionality using the demo script:
```bash
python parser/try.py
```

**What it does:**
- Opens Google's reCAPTCHA v2 demo page
- Automatically attempts to solve the captcha using PyPasser
- Clicks the submit button if successful
- Shows "SUCCESS" or "FAIL" message

**Use this to:**
- Verify PyPasser is working correctly
- Test your Chrome/Chromium installation
- Check anti-detection settings
- Understand captcha solving process before using main script

**Expected output:**
```
Setting up Chrome driver...
[INFO] pypasser patched successfully
Running pypasser...
SUCCESS
```

### Basic Run
```bash
python main.py
```

### What Happens

1. **Login** - Automatically logs in with provided email
2. **Captcha Detection** - Checks for reCAPTCHA v2
3. **Captcha Solving** - Attempts automatic solving (30-120 seconds)
   - If automatic fails → switches to manual mode (3 minutes timeout)
4. **Question Loop** - For each question:
   - Extracts text from page using CSS selector
   - Sends text to Ollama for AI analysis
   - Clicks "Yes" button if text is good (true)
   - Clicks "No" button if text is bad (false)
   - Handles captcha if it appears again
   - Waits for new question to load
5. **Progress Saving** - Saves progress after each question
6. **Auto-Restart** - Automatically restarts on critical errors

### Progress Tracking

If the program crashes or is interrupted:
- Progress is saved in `progress.json`
- Next run automatically resumes from the last completed question
- No need to start from scratch

### Manual Captcha Solving

If automatic captcha solving fails:
```
==================================================================
  MANUAL CAPTCHA SOLVING REQUIRED
==================================================================
  Please solve the captcha in the browser.
  You have 3 minute(s) and 0 seconds.
  The program will continue automatically.
==================================================================
```

Simply solve the captcha in the browser window - the program will detect completion and continue.

## 📊 Project Structure
```
.
├── main.py                        # Entry point and main logic
├── config.py                      # Configuration file (create this)
├── requirements.txt               # Python dependencies
├── progress.json                  # Progress tracker (auto-generated)
│
├── parser/
│   ├── __init__.py
│   ├── parse.py                   # Text parsing and answer logic
│   ├── capcha_solver.py           # reCAPTCHA detection and solving
│   ├── trash_detector.py          # Language detection (deprecated)
│   └── try.py                     # Captcha solving demo (test this first!)
│
├── ollama/
│   ├── __init__.py
│   └── ollama.py                  # Ollama API integration
│
├── .github/
│   └── ISSUE_TEMPLATE/
│       └── bug_report.md          # Bug report template
│
└── .idea/                         # PyCharm project files
```

## 🔧 How It Works

### 1. Login Flow
```python
UserLogin.user_login()
├── Navigate to login URL
├── Enter email
├── Check for captcha
├── Solve captcha if present
└── Click submit button
```

### 2. Text Classification Flow
```python
NewPageAnswer.click_answer()
├── Parse text from page (BeautifulSoup4)
├── Send to Ollama for analysis
├── Receive true/false response
├── Click appropriate button (Yes/No)
├── Check for captcha
└── Wait for new question
```

### 3. Captcha Solving Strategy
```python
CapchaSolver.if_captcha()
├── Detect reCAPTCHA iframe
├── Try automatic solving (PyPasser)
│   ├── Success → Continue
│   └── Fail → Manual mode
├── Manual mode (3 min timeout)
│   └── Wait for user to solve
└── Click "Continue" button
```

### 4. Ollama Integration
```python
OllamaTextAnalyzer.analyze()
├── Construct prompt with system message
├── Send to Ollama API (localhost:11434)
├── Parse response (true/false/yes/no/ano/nie)
└── Return boolean result
```

## 🐛 Troubleshooting

### Testing with try.py Demo

If `parser/try.py` fails:

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

**Always test captcha solving first!** Run `python parser/try.py` before attempting the main program. This will:
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

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚖️ Legal Disclaimer

This tool is for **educational purposes only**. Users are responsible for:
- Complying with website Terms of Service
- Respecting robots.txt and rate limits
- Obtaining necessary permissions
- Following local laws and regulations

The authors assume no liability for misuse.

## 👥 Authors

## *yvhdpdngr276* 


## 🔗 Useful Links

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [PyPasser GitHub](https://github.com/xHossein/PyPasser)
- [reCAPTCHA Documentation](https://developers.google.com/recaptcha)

---

**Last Updated:** November 2025

**Version:** 1.0.0
