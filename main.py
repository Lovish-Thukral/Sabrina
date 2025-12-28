from llama_cpp import Llama
from helpers.MessagesContainer import save_history
from Core.PromptGenerator import chat_prompt_InOut

# ------------------------
# init model
# ------------------------

MODEL_PATH = "./models/Qwen/qwen2.5-coder-7b-instruct-q5_k_m.gguf"
agent = Llama(
    model_path=MODEL_PATH,
    n_ctx=8192,
    n_threads=8,
    n_gpu_layers=28,
    temperature=0.1,
    verbose=False
)



def on_chat():
          while True:
               user_input = input("ask anything : ").strip()
               if user_input.lower() in {"exit", "quit"}:
                    reply = chat_prompt_InOut(agent=agent, temperature=0.5, input="User Left the Chat, Name this convo in 1 word for saving it")
                    save_history(reply)
                    break
               reply = chat_prompt_InOut(agent=agent, temperature=0.1, input=user_input)
               print(reply)      

on_chat()