from flask import Flask, render_template, request, redirect, url_for, session, flash
from pathlib import Path
import csv
import re
from datetime import datetime
from model_utils import load_or_train_model, analyze_message

app = Flask(__name__)
app.secret_key = "change-this-demo-secret-key"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "scan_history.csv"
MODEL, VECTORIZER, MODEL_NOTE = load_or_train_model(BASE_DIR)

def save_history(message, result):
    DATA_DIR.mkdir(exist_ok=True)
    new_file = not HISTORY_FILE.exists()
    with HISTORY_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["timestamp", "message_preview", "risk_label", "model_score", "warning_count"])
        preview = re.sub(r"\s+", " ", message)[:120]
        writer.writerow([datetime.now().isoformat(timespec="seconds"), preview,
                         result["label"], result["model_score"], len(result["warnings"])])

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    message = ""
    if request.method == "POST":
        message = request.form.get("message", "").strip()
        if not message:
            flash("Please enter a message before analyzing.", "error")
        elif len(message) > 10000:
            flash("Please keep the message under 10,000 characters.", "error")
        else:
            result = analyze_message(message, MODEL, VECTORIZER)
            save_history(message, result)
    return render_template("index.html", result=result, message=message, model_note=MODEL_NOTE)

@app.route("/history")
def history():
    rows = []
    if HISTORY_FILE.exists():
        with HISTORY_FILE.open("r", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    rows.reverse()
    return render_template("history.html", rows=rows[:50])

@app.route("/about")
def about():
    return render_template("about.html", model_note=MODEL_NOTE)

if __name__ == "__main__":
    app.run(debug=True)
