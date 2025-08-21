# DayMaker — Habit‑Aware To‑Do Suggester

A clean Flask + HTML/CSS/JS app that turns your daily habits into **5 useful, achievable actions** for today.  
Powered by a lightweight **NLP/ML engine** that:
- extracts keywords from your free‑text habits,
- maps them to curated task templates,
- and **learns from feedback** (👍/👎) to personalise future suggestions.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install flask
python app.py
```
Open http://localhost:5000

> No heavy ML dependencies required. All logic is self‑contained.

## How it learns
- When you thumbs‑up a suggestion, the app strengthens the association between the habit keywords and that task.  
- Thumbs‑down weakens it.  
- Learning is stored in `data/learned.json` so it persists across sessions.

## Structure
```
todo_suggester_app/
├─ app.py
├─ models/
│  └─ suggester.py
├─ data/
│  ├─ seed_rules.json
│  └─ learned.json
├─ templates/
│  └─ index.html
└─ static/
   ├─ style.css
   └─ script.js
```

## Customising
- Edit `data/seed_rules.json` to add your own habit keywords and task templates.
- Tweak ranking in `models/suggester.py` (`_score_task`) to weigh coverage/similarity differently.
- Brand the UI by adjusting `static/style.css`.

## Notes
- This project is intentionally dependency‑light to be easy to run anywhere.
- You can later swap in a vector model or TF‑IDF library if you prefer.
- Created on 2025-08-21.
