import json
import os

MAX_MESSAGES = 10
MESSAGES = []
HISTORY_CONTAINER = []


def add_message(role,content):
    if len(MESSAGES) >= MAX_MESSAGES:
        MESSAGES.pop(1) # Removing Oldest Message after system prompt
    MESSAGES.append({"role" : role, "Content" : content})
    HISTORY_CONTAINER.append({"role" : role, "Content" : content})


def save_history(filename):
    # 1. Define the full path
    path = f"/home/nullbyte/Desktop/Sabrina/ConversationHistory/{filename}.txt"
    # 2. (Recommended) Ensure the directory exists to avoid FileNotFoundError
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # 3. Save the file (Fixed 'indent' capitalization)
    with open(path, "w") as f:
        json.dump(HISTORY_CONTAINER, f, indent=4)



