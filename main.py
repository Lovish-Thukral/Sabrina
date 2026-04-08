from llama_cpp import Llama
from helpers import save_history, HISTORY_CONTAINER, get_current_screen
from Core import chat_prompt_gen, Command_Executer, error_handler
from Tools import Pre_Executor
from GUI import MainWindow
from STT import STT
from TTS import TTS
import os
import json

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

class Sabrina:
    """
Core program to run the application.

Allows loading a language model from either a local path or a Hugging Face repository.

Args:
    llmLocation (str): Path to the local model file
    llm_repo_id (str): Hugging Face repository ID
    llm_filename (str): Model filename in the repository
"""
    def __init__(
        self,
        local_model_path="null",
    ):
        self.device_info = decider()
        self.model_info = self.device_info.get("models", {})
        self.agent = self.load_model(repo_id=self.model_info["repo"], filename=self.model_info["model"], localpath= local_model_path)
        self.stt = STT(model_size=self.model_info["stt"], device="cuda" if self.device_info.get("gpu", False) else "cpu")
        self.stt.start()
        self.tts = TTS()
        self.tts.start()
        self.noinput = 0

    def load_model(self, localpath, repo_id, filename):
        n_gpu_layers = -1
        if localpath.endswith(".gguf") and os.path.isfile(localpath):
            return Llama(
                model_path=localpath,
                n_ctx=8192,
                n_threads=4,
                n_gpu_layers=n_gpu_layers,
                temperature=0.1,
                verbose=False
            )
        else:
            try:
                return Llama.from_pretrained(
                    repo_id=repo_id,
                    filename=filename,
                    n_ctx=8192,
                    n_threads=4,
                    n_gpu_layers=n_gpu_layers,
                    temperature=0.1,
                    verbose=False
                )
            except Exception as e:
                raise RuntimeError(f"Model loading failed: {e}")
    
    def responsed(self, inputData):
        "Creates Response for the User Input"

        if not inputData:
            self.noinput += 1

            if self.noinput == 3:
                inputData = "user left the chat, say a flirtatious goodbye"
            else:
                inputData = "Ask User to Repeat the Command, as No Input Detected"
        else:
            self.noinput = 0 

        try:
            print(f"Received User Input: {inputData}")

            System = Pre_Executor(agent=self.agent, input=inputData)
            currunt_screen = get_current_screen()

            prompt = f"Currunt Screen: {currunt_screen} \n User: {inputData} \n System:{System}"
            print(prompt)

            response = chat_prompt_gen(agent=self.agent, input=prompt, noinput=self.noinput)

            print(response["TTS"])
            self.tts.play(response["TTS"])

            if self.noinput == 3:
                System = {"terminate": True}
            return {
                "response": response,
                "System": System
            }
        except Exception as e:
            print(f"Error in processing input: {e}")
            return {
                "response": {
                    "TTS": "Sorry, I encountered an error while processing your request."
                },
                "System": {}
            }

    def execute(self, command, window):
        "Executes the Command Generated by the Model, and Handles Errors if Occured"
        if not command:
            return {
                "Status": "Failed",
                "response": "No command provided"
            }
        response = Command_Executer(Command=command)
        HISTORY_CONTAINER.append({"Shell Status:" : response["Status"], "Shell Response": response["Response"]})
        if response["Status"] == "Failed":
            errorfound = response.get("Error_Found", "No error info")
            window.set_error(f"Command execution failed: {errorfound}")
            error_info = f"Command: {command} \n Error_Found: {errorfound}"
            debug_response = error_handler(agent=self.agent, err=error_info, STT=self.stt, TTS=self.tts)
            return debug_response
        return response
    
    def stop(self):
        "Stops the Application"
        self.tts.stop()
        self.stt.stop()
        self.agent = None
        return
    
    def run(self):
        "Runs the Application"
        win = MainWindow(self.stop)
        win.show()
        while True:
            win.set_listening()
            input_data = self.stt.listen()
            win.set_responding()
            response = self.responsed(input_data)
            print(f"Generated Response: {response}")  # Debug statement to check response
            command = response.get("response", {}).get("CMND", "NONE")
            if command != "NONE":
                shell = self.execute(command, window=win)
                response = self.responsed(f"System: Execution Completed \n Result: {shell}")
            if response.get("System", {}).get("terminate", False):
                break
        save_history()

    
if __name__ == "__main__":
    sabrina = Sabrina()
    sabrina.run()
    sabrina.stop()