import json
import os

SETTINGS_FILE = "settings2.json"
LEADERBOARD_FILE = "leaderboard2.json"

def load_settings():
    defaults = {"sound": True, "color": [0, 100, 255], "difficulty": "normal"}
    if not os.path.exists(SETTINGS_FILE):
        save_json(SETTINGS_FILE, defaults)
        return defaults
    try:
        data = json.load(open(SETTINGS_FILE, "r"))
        for k,v in defaults.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return defaults

def save_settings(settings):
    save_json(SETTINGS_FILE, settings)

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        save_json(LEADERBOARD_FILE, [])
    try:
        return json.load(open(LEADERBOARD_FILE, "r"))
    except Exception:
        return []

def save_leaderboard_entry(user, score, dist):
    data = load_leaderboard()
    data.append({"user": user, "score": score, "distance": dist})
    data = sorted(data, key=lambda x: x["score"], reverse=True)[:10]
    save_json(LEADERBOARD_FILE, data)
