import json
import os

MAX_MESSAGES = 20
MESSAGES = []
HISTORY_CONTAINER = []


def add_message(role,content):
    if len(MESSAGES) >= MAX_MESSAGES:
        MESSAGES.pop(0) # Removing Oldest Message after system prompt
    MESSAGES.append({"role" : role, "content" : content})
    HISTORY_CONTAINER.append({"role" : role, "content" : content})


def save_history(filename):
    # 1. Define the full path
    path = f"/home/nullbyte/Desktop/Sabrina/ConversationHistory/{filename}.txt"
    # 2. (Recommended) Ensure the directory exists to avoid FileNotFoundError
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # 3. Save the file (Fixed 'indent' capitalization)
    with open(path, "w") as f:
        json.dump(HISTORY_CONTAINER, f, indent=4)

def message_to_prompt():
    prompt = ""
    for msg in MESSAGES:
        role = msg["role"]
        content = msg["content"]
        prompt += f"<|im_start|>{role}\n{content}\n<|im_end|>\n"
    return prompt.strip()


