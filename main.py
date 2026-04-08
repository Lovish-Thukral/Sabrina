# main.py
import os
import json
from llama_cpp import Llama
from helpers import save_history, HISTORY_CONTAINER, get_current_screen
from Core import chat_prompt_gen, Command_Executer, error_handler
from Tools import Pre_Executor
from GUI import MainWindow
from STT import STT
from TTS import TTS


def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


models = {
    "8": {
        "repo": "Qwen/Qwen2.5-7B-Instruct-GGUF",
        "model": "qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf",
        "stt": "medium.en"
    },
    "6": {
        "repo": "Qwen/Qwen2.5-3B-Instruct-GGUF",
        "model": "qwen2.5-3b-instruct-q6_k.gguf",
        "stt": "medium.en"
    },
    "4": {
        "repo": "Qwen/Qwen2.5-3B-Instruct-GGUF",
        "model": "qwen2.5-3b-instruct-q4_k_m.gguf",
        "stt": "small.en"
    },
    "macro_model": {
        "repo": "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        "model": "qwen2.5-1.5b-instruct-q5_k_m.gguf",
        "stt": "small.en"
    }
}


def decider():
    with open("UserPreferences/userMetaData.json", "r") as f:
        data = json.load(f)

    user = data.get("user", {})
    if not user:
        raise ValueError("User information not found in UserMetaData.json, re-execute install.sh.")

    gpu = user.get("vram")
    cpu = user.get("total_ram")
    model_info = None
    gpu_available = False  # default

    if gpu not in (None, "N/A", "Unknown"):
        gpu_available = True
        gpu = safe_int(gpu)
        if gpu >= 8000:
            model_info = models["8"]
        elif gpu >= 6000:
            model_info = models["6"]
        elif gpu >= 4000:
            model_info = models["4"]

    if cpu in (None, "N/A", "Unknown"):
        raise ValueError("CPU information not found in UserMetaData.json, re-execute install.sh.")

    cpu = safe_int(cpu)
    if cpu >= 15000:
        model_info = models["6"]
    elif cpu >= 11000:
        model_info = models["4"]
    else:
        model_info = models["macro_model"]

    return {"models": model_info, "gpu": gpu_available}


class Sabrina:
    def __init__(self, local_model_path="null"):
        # 1. UI first — visible immediately so user knows app started
        self.win = MainWindow(stop_callback=self.stop)
        self.win.show()

        # 2. Load everything else after UI is up
        self.device_info = decider()
        self.model_info = self.device_info.get("models", {})

        self.agent = self.load_model(
            repo_id=self.model_info["repo"],
            filename=self.model_info["model"],
            localpath=local_model_path
        )
        self.stt = STT(
            model_size=self.model_info["stt"],
            device="cuda" if self.device_info.get("gpu", False) else "cpu"
        )
        self.stt.start()
        self.tts = TTS()
        self.tts.start()
        self.noinput = 0
        self.win.set_ready()  

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
            current_screen = get_current_screen()
            prompt = f"Current Screen: {current_screen}\nUser: {inputData}\nSystem: {System}"
            print(prompt)

            response = chat_prompt_gen(agent=self.agent, input=prompt, noinput=self.noinput)
            print(response)
            print(response["TTS"])
            self.tts.play(response["TTS"])
            if self.noinput == 3:
                System = {"terminate": True}
            return {"response": response, "System": System}

        except Exception as e:
            print(f"Error in processing input: {e}")
            self.win.set_error(f"Processing error: {e}")
            return {
                "response": {"TTS": "Sorry, I encountered an error while processing your request."},
                "System": {}
            }

    def execute(self, command):
        if not command:
            return {"Status": "Failed", "response": "No command provided"}

        response = Command_Executer(Command=command)
        HISTORY_CONTAINER.append({"Shell Status:": response["Status"], "Shell Response": response["Response"]})

        if response["Status"] == "Failed":
            errorfound = response.get("Error_Found", "No error info")
            self.win.set_error(f"Command execution failed: {errorfound}")
            error_info = f"Command: {command}\nError_Found: {errorfound}"
            return error_handler(agent=self.agent, err=error_info, STT=self.stt, TTS=self.tts)

        return response

    def stop(self):
        self.tts.stop()
        self.stt.stop()
        self.agent = None

    def run(self):
        while True:
            self.win.set_listening()
            input_data = self.stt.listen()
            self.win.set_responding()
            response = self.responsed(input_data)
            print(f"Generated Response: {response}")
            command = response.get("response", {}).get("CMND", "NONE")
            # if command != "NONE":
                # shell = self.execute(command)
                # response = self.responsed(f"System: Execution Completed\nResult: {shell}")

            if response.get("System", {}).get("terminate", False):
                break

        save_history()


if __name__ == "__main__":
    sabrina = Sabrina()
    sabrina.run()
    sabrina.stop()