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
    if(len(MESSAGES) > 2) :
        path = f"/home/nullbyte/Desktop/Sabrina/ConversationHistory/{filename}.txt"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(HISTORY_CONTAINER, f, indent=4)
    else : 
        print("No Coversation Found Exiting without saving")

def message_to_prompt():
    prompt = ""
    for msg in MESSAGES:
        role = msg["role"]
        content = msg["content"]
        prompt += f"<|im_start|>{role}\n{content}\n<|im_end|>\n"
    return prompt.strip()


