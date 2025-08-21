import json
import os
import math
import re
from collections import Counter, defaultdict

STOPWORDS = set("""
a an the of to and in on for with at from by about as into like through after over
between out against during without before under around among is are was were be been being
do does did doing have has had having can could should would will may might must
i you he she it we they me him her us them my your his her its our their
this that these those here there then than too very just not no nor only same so
""".split())

token_re = re.compile(r"[a-z']+")

def tokenize(text):
    text = text.lower()
    tokens = token_re.findall(text)
    return [t for t in tokens if t not in STOPWORDS]

def keyword_counts(text):
    return Counter(tokenize(text))

def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

class HabitSuggester:
    """
    Lightweight NLP/ML hybrid:
      - Keyword-based candidate generation from seed_rules.json
      - Learns from feedback by strengthening associations in learned.json
      - Ranks candidates by keyword coverage + learned weights + simple Jaccard similarity
    Works without external libraries.
    """
    def __init__(self, rules_path="data/seed_rules.json", learned_path="data/learned.json"):
        self.rules_path = rules_path
        self.learned_path = learned_path
        self.rules = self._load_json(self.rules_path, default={"rules": {}})
        self.learned = self._load_json(self.learned_path, default={"associations": {}, "seen": 0})
        # Normalize keys
        self.rules["rules"] = {k.lower(): v for k, v in self.rules.get("rules", {}).items()}

    def _load_json(self, path, default):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return default
        return default

    def _save_json(self, path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _rule_candidates(self, tokens):
        cands = []
        token_set = set(tokens)
        for kw, tasks in self.rules.get("rules", {}).items():
            # simple contain / prefix match
            if kw in token_set or any(t.startswith(kw) or kw.startswith(t) for t in token_set):
                for t in tasks:
                    cands.append(("rule", kw, t))
        return cands

    def _learned_candidates(self, tokens):
        cands = []
        assoc = self.learned.get("associations", {})
        for tok in set(tokens):
            if tok in assoc:
                for task, weight in assoc[tok].items():
                    cands.append(("learned", tok, task, weight))
        return cands

    def _score_task(self, habits_tokens, task, contributing_tokens, learned_weight):
        # base from coverage
        coverage = len(contributing_tokens)
        # jaccard between keywords and task tokens
        task_tokens = set(tokenize(task))
        sim = jaccard(set(habits_tokens), task_tokens)
        # total score
        return 0.6 * coverage + 0.3 * sim + 0.1 * learned_weight

    def suggest(self, habits_text, k=5):
        tokens = tokenize(habits_text)
        if not tokens:
            # generic starter pack
            return [
                "Schedule 25 minutes for focused work (Pomodoro)",
                "Plan today in 3 bullets (must/should/nice-to-have)",
                "Tidy your workspace for 5 minutes",
                "Walk for 10–15 minutes outside",
                "Inbox zero sweep: archive or reply to 5 emails",
            ]
        # Gather candidates
        rule_cands = self._rule_candidates(tokens)
        learned_cands = self._learned_candidates(tokens)

        # Aggregate and score
        contributions = defaultdict(set)  # task -> tokens that triggered it
        learned_weights = defaultdict(float)  # task -> sum weights

        for _, kw, task in rule_cands:
            contributions[task].add(kw)
        for _, tok, task, weight in learned_cands:
            contributions[task].add(tok)
            learned_weights[task] += weight

        # Add a few generic tasks always
        generic_pool = [
            "Plan your top 3 priorities for today",
            "Do a 10-minute stretch or mobility routine",
            "Drink a glass of water and refill your bottle",
            "Declutter one small area (desk, downloads folder)",
            "Review calendar & block focus time",
        ]
        for g in generic_pool:
            contributions.setdefault(g, set())

        # score
        scored = []
        for task, toks in contributions.items():
            lw = learned_weights.get(task, 0.0)
            s = self._score_task(tokens, task, toks, lw)
            scored.append((s, task))

        scored.sort(reverse=True)
        # dedupe by simple normalized text
        seen = set()
        results = []
        for _, t in scored:
            key = t.strip().lower()
            if key not in seen:
                seen.add(key)
                results.append(t)
            if len(results) >= k:
                break
        return results

    def update_feedback(self, habits_text, task, rating):
        """
        rating: +1 (helpful) or -1 (not helpful)
        """
        rating = 1 if rating >= 1 else -1
        tokens = set(tokenize(habits_text))
        assoc = self.learned.setdefault("associations", {})
        for tok in tokens:
            tok_assoc = assoc.setdefault(tok, {})
            tok_assoc[task] = tok_assoc.get(task, 0.0) + rating
        self.learned["seen"] = int(self.learned.get("seen", 0)) + 1
        # prune very negative or zero-weight edges occasionally
        if self.learned["seen"] % 25 == 0:
            for tok, m in list(assoc.items()):
                for t, w in list(m.items()):
                    if w <= -3:
                        del m[t]
                if not m:
                    del assoc[tok]
        self._save_json(self.learned_path, self.learned)
        return True
