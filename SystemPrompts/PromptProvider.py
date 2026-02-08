from pathlib import Path
from datetime import datetime
import json
from helpers.MessagesContainer import message_to_prompt


# ------------------------
# Paths (robust resolution from Core/)
# ------------------------
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

SHELL_PROMPT_PATH = PROJECT_ROOT / "SystemPrompts" / "ShellRules.txt"
MODEL_RULES_PATH = PROJECT_ROOT / "SystemPrompts" / "Formatter&Rules.txt"
USER_METADATA_PATH = PROJECT_ROOT / "UserPrefrences" / "userMataData.json"
FUNCTIONAL_ANALYSIS_PATH = PROJECT_ROOT / "SystemPrompts" / "FunctionAnalysis.txt"

# Verify files exist
for path_name, path in [
    ("MODEL_RULES", MODEL_RULES_PATH),
    ("USER_METADATA", USER_METADATA_PATH),
    ("SHELL_PROMPT", SHELL_PROMPT_PATH),
    ("FUNCTIONAL_ANALYSIS", FUNCTIONAL_ANALYSIS_PATH)
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

with open(FUNCTIONAL_ANALYSIS_PATH, 'r') as f:
    ANALYSIS_RULES = f.read().strip()


# ------------------------
# Extract User Metadata from JSON
# ------------------------
def format_user_metadata(meta: dict, request: str) -> str:
    lines = ['KNOWN USER INFO']
    user = meta.get("user", {})

    if (user and request == "user"):
        lines.append(f"- Name: {user.get('name', 'Unknown')}")
        lines.append(f"- Gender: {user.get("gender", "unknown")}")
        lines.append(f"- Operating System : {user.get('user_os', 'unknown')}")
        lines.append(f"- Default Shell: {user.get('default_shell', 'unknown')}")
    return "\n".join(lines)


# Build base system prompt (raw content)
SYSTEM_PROMPT_TEXT = "\n".join([
    MODEL_RULES,
    format_user_metadata(USER_METADATA, "user"),
])

SHELL_PROMPT_TEXT = "\n".join([
    SHELL_RULES,
    format_user_metadata(USER_METADATA, "user")
])
# ------------------------
# System Prompt Generator
# ------------------------

def system_prompt(isboot = False) -> str:
    """Generate initial system greeting prompt"""
    
    if isboot:
        task = f"<No Command, just TTS> Greet user GM/GN for date {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")} and ask about his/her day, don't mention time."
    else:
        task = "<No Command, just TTS>  user said Hi!"

    print(task)
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

def functional_prompt(prompt:str) -> str:
    return f"""
<|im_start|>system
{ANALYSIS_RULES}
<|im_end|>
User: Bye, stop this conversation now
Output: [terminatesession]

User: What’s the weather today?
Output: [weather(Currunt,today)]

User: Tell me the weather on 5th February
Output: [weather(New York, 2026-02-05)]

User: Do you remember my favourite color?
Output: [preference([favourite_color, favorite_color, color_preference, preferred_color])]

User: My favourite programming language is Python
Output: [save_Preference(favourite_programming_language, Python)]

User: Check if you know my favourite weather and also tell me today's weather
Output: [preference([favourite_weather, favorite_weather, weather_preference, preferred_weather]), weather(Amritsar,today)]

User: I like rainy weather, remember that and tell me the weather today
Output: [save_preference(favourite_weather, rainy), weather(Current,today)]

User: explain me the best book to be rich
Output: []

User: Remember this: I hate hot weather
Output: [save_preference(dislikedweather, hotweather)]

User: Terminate the session immediately
Output: [terminatesession]

User: what is my fav word app ?
Output: [prefrence([fav_word_app, fav_wordapp, fav_word_application, default_word_app])]
 
User: What is my fav browser ?
Output: [prefrence([fav_browser, favrouite_browser, default_browser])]

{prompt}
<|im_start|>assistant
""".strip()