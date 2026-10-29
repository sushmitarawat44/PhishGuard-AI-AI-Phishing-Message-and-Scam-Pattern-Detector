# PhishGuard AI — MCA AI Tools Mini Project

## Overview
PhishGuard AI is an educational phishing-message screening prototype. It combines a local TF-IDF + Logistic Regression classifier with transparent pattern rules for suspicious urgency, requests for credentials/OTP, prize claims, payment pressure, and URLs.

**No paid AI API is required.** The model trains locally when the Flask app starts using the bundled illustrative dataset.

## Requirements
- Python 3.10 or newer
- Internet only for installing packages (unless already installed)
- A modern browser

## Run on Windows
1. Extract the ZIP.
2. Open Command Prompt or PowerShell in the `PhishGuard_AI` folder.
3. Create an environment (recommended):
   `py -m venv .venv`
4. Activate it:
   PowerShell: `.\.venv\Scripts\Activate.ps1`
   Command Prompt: `.venv\Scripts\activate.bat`
5. Install dependencies:
   `python -m pip install -r requirements.txt`
6. Start:
   `python app.py`
7. Open `http://127.0.0.1:5000` in your browser.
8. Try both built-in sample messages and capture screenshots for the report.

If `py` is not recognized, try `python` instead.

## Run on macOS/Linux
`python3 -m venv .venv`
`source .venv/bin/activate`
`python -m pip install -r requirements.txt`
`python app.py`
Then open `http://127.0.0.1:5000`.

## Main files
- `app.py` — Flask routes, history logging
- `model_utils.py` — model training and message analysis
- `data/messages.csv` — small illustrative labelled dataset
- `templates/` — HTML pages
- `static/style.css` — responsive styling
- `data/scan_history.csv` — created after first scan

## Test cases
1. Suspicious: "URGENT your account will be suspended. Verify your password and OTP at http://example.test"
2. Ordinary: "Hi team, our project meeting is scheduled for 2 PM tomorrow in Lab 3."
3. Empty message: should show a validation warning.
4. Long message above 10,000 characters: should be rejected.
5. History: after analysis, open History and verify the scan appears.

## Important limitations
The included dataset contains synthetic, illustrative examples. It is not a benchmark dataset and is too small to support real-world accuracy claims. The risk score is a heuristic indicator, not a calibrated probability. The app does not verify sender identity, inspect actual website destinations, or replace security tools. A low score does not mean a message is safe.

## Troubleshooting
- If package installation fails, check internet connection and Python version.
- If port 5000 is occupied, change `app.run(debug=True)` to `app.run(debug=True, port=5001)` and open port 5001.
- If a module is missing, activate the virtual environment and run `python -m pip install -r requirements.txt`.
