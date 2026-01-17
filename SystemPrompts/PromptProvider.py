from pathlib import Path
from datetime import datetime
import json

from helpers.MessagesContainer import message_to_prompt
from helpers.MataDataFormatter import format_user_metadata

# ------------------------
# Paths (robust resolution from Core/)
# ------------------------
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

SHELL_PROMPT_PATH = PROJECT_ROOT / "SystemPrompts" / "ShellRules.txt"
MODEL_RULES_PATH = PROJECT_ROOT / "SystemPrompts" / "Formatter&Rules.txt"
USER_METADATA_PATH = PROJECT_ROOT / "UserPrefrences" / "userMataData.json"

# Verify files exist
for path_name, path in [
    ("MODEL_RULES", MODEL_RULES_PATH),
    ("USER_METADATA", USER_METADATA_PATH),
    ("SHELL_PROMPT", SHELL_PROMPT_PATH)
]:
    if not path.exists():
        raise FileNotFoundError(f"{path_name}: {path}")

# ------------------------
# Load static files
# ------------------------

with open(MODEL_RULES_PATH, "r") as f:
    MODEL_RULES = f.read().strip()

with open(USER_METADATA_PATH, "r") as f:
    USER_METADATA = json.load(f)

with open(SHELL_PROMPT_PATH, "r") as f:
    SHELL_RULES = f.read().strip()

# Build base system prompt (raw content)
SYSTEM_PROMPT_TEXT = "\n".join([
    MODEL_RULES,
    format_user_metadata(USER_METADATA, "system"),
    format_user_metadata(USER_METADATA, "user"),
])

SHELL_PROMPT_TEXT = "\n".join([
    SHELL_RULES,
    format_user_metadata(USER_METADATA, "system"),
    format_user_metadata(USER_METADATA, "user"),
    # format_user_metadata(USER_METADATA, "prefrences")

])
# ------------------------
# System Prompt Generator
# ------------------------

def system_prompt(isboot = False) -> str:
    """Generate initial system greeting prompt"""
    
    if isboot:
        task = f"<No Command, just TTS> Greet user GM/GN for date {datetime.now().strftime("%Y-%m-%d")} and ask about his/her day, don't mention time."
    else:
        task = "<No Command, just TTS>  user said Hi!"

    return f"""
<|im_start|>system
{SYSTEM_PROMPT_TEXT}
<|im_end|>
TASK: {task}
<|im_start|>assistant
""".strip()


# ------------------------
# chat Prompt Generator
# ------------------------

def chat_prompt() -> str:
    chat_history = message_to_prompt() or ""
    
    return f"""
<|im_start|>system
{SYSTEM_PROMPT_TEXT}
<|im_end|>
{chat_history}
<|im_start|>assistant
""".strip()

def shell_prompt(logs:str) -> str:
    chat_history = message_to_prompt() or ""
    return f"""
<|im_start|>system
{SHELL_PROMPT_TEXT}
<|im_end|>
{chat_history + logs}
<|im_start|>assistant
""".strip()