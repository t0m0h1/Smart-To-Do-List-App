from flask import Flask, render_template, request, jsonify
from models.suggester import HabitSuggester
import os

app = Flask(__name__)
suggester = HabitSuggester(
    rules_path=os.path.join("data", "seed_rules.json"),
    learned_path=os.path.join("data", "learned.json"),
)

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/suggest")
def suggest():
    data = request.get_json(force=True) or {}
    habits = data.get("habits", "")
    suggestions = suggester.suggest(habits, k=5)
    return jsonify({"suggestions": suggestions})

@app.post("/feedback")
def feedback():
    data = request.get_json(force=True) or {}
    habits = data.get("habits", "")
    task = data.get("task", "")
    rating = int(data.get("rating", 0))  # +1 or -1 expected
    ok = suggester.update_feedback(habits, task, rating)
    return jsonify({"ok": ok})

if __name__ == "__main__":
    # For local dev. In production, use a proper WSGI server.
    app.run(debug=True, host="0.0.0.0", port=5000)
