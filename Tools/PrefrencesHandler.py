import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.absolute()
USER_METADATA_PATH = PROJECT_ROOT / "UserPrefrences" / "userMataData.json"
TEMP_PATH = PROJECT_ROOT / "UserPrefrences" / "temp.json"


def preference_checker(keys: list) -> str:
    """
    Return the value of the first matching key from the user's preferences.
    Args:
        keys (list[str]): List of preference keys to check.
    Returns:
        Value[str]: The matched preference value, or None if not found.
    """
     
    with open(USER_METADATA_PATH, "r") as f:
        user_metadata = json.load(f)

    preferences = user_metadata.get("preferences", {})

    if not preferences:
        raise ValueError("Preferences not found in metadata")

    for key in keys:
        value = preferences.get(key)
        if value:
            return value

    return None

def save_preference(key: str, value) -> str:
    try:
        if USER_METADATA_PATH.exists():
            with open(USER_METADATA_PATH, "r") as f:
                user_metadata = json.load(f)
        else:
            user_metadata = {}

        user_metadata.setdefault("preferences", {})
        user_metadata["preferences"][key] = value

        # Write updated data to temp file
        with open(TEMP_PATH, "w") as f:
            json.dump(user_metadata, f, indent=4)

        # Atomically replace original
        os.replace(TEMP_PATH, USER_METADATA_PATH)

        return f"Saved '{key}' as '{value}' in database."

    except Exception:
        return "Error Saving Preferences"