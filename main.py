from llama_cpp import Llama
import json
from datetime import datetime

from helpers.MataDataFormatter import format_user_metadata
from helpers.MessagesContainer import add_message, save_history, MESSAGES

# ------------------------
# Paths (dev)
# ------------------------
MODEL_PATH = "./models/Qwen/qwen2.5-coder-7b-instruct-q5_k_m.gguf"
SYSTEM_PROMPT_PATH = "./SystemPrompts/main.txt"
MODEL_RULES_PATH = "./SystemPrompts/Formatter&Rules.txt"
USER_METADATA_PATH = "./UserPrefrences/userMataData.json"

# ------------------------
# Load static files
# ------------------------
with open(SYSTEM_PROMPT_PATH, "r") as f:
    MODEL_IDENTITY = f.read().strip()

with open(MODEL_RULES_PATH, "r") as f:
    MODEL_RULES = f.read().strip()

with open(USER_METADATA_PATH, "r") as f:
    USER_METADATA = json.load(f)

# ------------------------
# Build ONE system prompt
# ------------------------
SYSTEM_PROMPT_TEXT = "\n".join([
    MODEL_IDENTITY,
    MODEL_RULES,
    format_user_metadata(USER_METADATA, "system"),
    format_user_metadata(USER_METADATA, "user"),
])

BASE_SYSTEM_PROMPT = f"""
<|im_start|>system
{SYSTEM_PROMPT_TEXT}
<|im_end|>
""".strip()

# ------------------------
# Init model (ONE instance)
# ------------------------
agent = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=8,
    n_gpu_layers=28,
    temperature=0.3,
    verbose=False
)

# ------------------------
# Session state
# ------------------------
session_prompt = BASE_SYSTEM_PROMPT + "\n<|im_start|>assistant\n"

# Log system prompt once
add_message(role="system", content=SYSTEM_PROMPT_TEXT)

# ------------------------
# Initial greeting
# ------------------------
def start_session():
    global session_prompt
    now = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    greeting_block = f"""
<|im_start|>user
CURRENT_SCREEN: TERMINAL
TASK: Greet hello to the user appropriately based on date {now} in India. Do not mention time.
PREVIOUS_OUTPUT: NONE
ERROR_FOUND: NONE
<|im_end|>
<|im_start|>assistant
"""

    session_prompt += greeting_block

    out = agent(
        prompt=session_prompt,
        max_tokens=128,
        stop=["<|im_end|>"]
    )

    reply = out["choices"][0]["text"].strip()
    print("Assistant:", reply)

    session_prompt += reply + "\n"

    add_message(role="assistant", content=reply)

# ------------------------
# Main chat loop
# ------------------------
def user_chat():
    global session_prompt

    try:
        while True:
            user_input = input("ask anything : ").strip()
            if user_input.lower() in {"exit", "quit"}:
                break

            user_block = f"""
<|im_start|>user
CURRENT_SCREEN: TERMINAL
TASK: {user_input}
PREVIOUS_OUTPUT: NONE
ERROR_FOUND: NONE
<|im_end|>
<|im_start|>assistant
"""

            session_prompt += user_block
            print(session_prompt)
            add_message(role="user", content=user_input)

            out = agent(
                prompt=session_prompt,
                max_tokens=128,
                stop=["<|im_end|>"]
            )

            reply = out["choices"][0]["text"].strip()
            print("Assistant:", reply)

            session_prompt += reply + "\n"
            add_message(role="assistant", content=reply)

    finally:
        save_history(MESSAGES)
        print("\nSession saved. Goodbye.")

# ------------------------
# Run
# ------------------------
start_session()
user_chat()
