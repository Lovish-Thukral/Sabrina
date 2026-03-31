import json

from huggingface_hub import model_info

def safe_int(value):
    """Safely converts a value to an integer, returning None if conversion fails."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

models = {
    "8": {
        "repo": "Qwen/Qwen2.5-7B-Instruct-GGUF",
        # ~5–6 GB VRAM (Q4_K_M, split file, requires both parts)
        "model": "qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf",
        "stt" : "medium.en"
    },

    "6": {
        "repo": "Qwen/Qwen2.5-3B-Instruct-GGUF",
        # ~3.5–4.5 GB VRAM (Q6, tighter but better quality than Q4)
        "model": "qwen2.5-3b-instruct-q6_k.gguf",
        "stt" : "medium.en"
    },

    "4": {
        "repo": "Qwen/Qwen2.5-3B-Instruct-GGUF",
        # ~2.5–3.5 GB VRAM (Q4_K_M, safe for 4GB GPUs)
        "model": "qwen2.5-3b-instruct-q4_k_m.gguf",
        "stt" : "small.en"
    },

    "macro_model": {
        "repo": "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        # ~1.5–2.5 GB VRAM (Q5_K_M, fallback, very safe)
        "model": "qwen2.5-1.5b-instruct-q5_k_m.gguf",
        "stt" : "small.en"
    }
}

def decider():
    """Decides which model to load based on system config."""
    with open("UserPreferences/userMetaData.json", "r") as f:
        data = json.load(f)

    user = data.get("user", {})
    if not user:
        raise ValueError(
            "User information not found in UserMetaData.json, re-execute install.sh. Nothing will download again."
        )

    gpu = user.get("vram")
    cpu = user.get("total_ram")
    model_info = None

    if gpu not in (None, "N/A", "Unknown"):
        gpu_available = True
        gpu = safe_int(gpu)
        if gpu >= 8000:
            model_info =  models["8"]
        elif gpu >= 6000:
            model_info = models["6"]
        elif gpu >= 4000:
            model_info = models["4"]
    if cpu in (None, "N/A", "Unknown"):
        raise ValueError(
            "CPU information not found in UserMetaData.json, re-execute install.sh. Nothing will download again."
        )
    cpu = safe_int(cpu)
    if cpu >= 15000:
        model_info = models["6"]
    elif cpu >= 11000:
        model_info = models["4"]
    else:
        model_info = models["macro_model"]
    return {
        "models": model_info,
        "gpu": gpu_available 
    }
    



print(decider())