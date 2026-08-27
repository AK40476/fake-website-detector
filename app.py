import json
from datetime import datetime
from flask import Flask, render_template, request
from modules.url_parser import parse_url
from modules.rule_engine import calculate_risk

import os
app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form['url'].strip().lower()
    
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    
    score, level, reasons = calculate_risk(url)

    # Save scan history
    history_file = os.path.join(os.getcwd(), "data", "history.json")

    try:
        with open(history_file, "r") as file:
            history = json.load(file)
    except:
        history = []

    # Remove old entry of same URL (avoid duplicates)
    history = [entry for entry in history if entry["url"] != url]

    history.append({
        "url": url,
        "score": score,
        "level": level,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # Keep only last 20 scans
    history = history[-20:]

    with open(history_file, "w") as file:
        json.dump(history, file, indent=4)

    display_score = score if score <= 100 else 100

    return render_template('result.html',
                           url=url,
                           score=display_score,
                           level=level,
                           reasons=reasons)

@app.route('/history')
def history():
    history_file = os.path.join(os.getcwd(), "data", "history.json")

    try:
        with open(history_file, "r") as file:
            history_data = json.load(file)
    except:
        history_data = []

    return render_template("history.html", history=history_data)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.get_json()

    if not data or "url" not in data:
        return {"error": "URL is required"}, 400

    url = data["url"]
    score, level, reasons = calculate_risk(url)

    display_score = score if score <= 100 else 100

    return {
        "url": url,
        "score": display_score,
        "level": level,
        "reasons": reasons
    }

if __name__ == '__main__':
    app.run(debug=True)
