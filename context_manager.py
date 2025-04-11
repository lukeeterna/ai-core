# context_manager.py

import os
import json

CONTEXT_DIR = os.path.expanduser("~/Desktop/ai-core/user_contexts")
os.makedirs(CONTEXT_DIR, exist_ok=True)

def _get_context_file(user_id):
    return os.path.join(CONTEXT_DIR, f"{user_id}.json")

def get_context(user_id):
    path = _get_context_file(user_id)
    if not os.path.exists(path):
        return ""
    with open(path, "r") as f:
        return json.load(f).get("history", "")

def update_context(user_id, prompt, response):
    path = _get_context_file(user_id)
    history = get_context(user_id)
    new_entry = f"\nUser: {prompt}\nAI: {response}"
    with open(path, "w") as f:
        json.dump({"history": history + new_entry}, f)

def reset_context(user_id):
    path = _get_context_file(user_id)
    if os.path.exists(path):
        os.remove(path)