from llama_cpp import Llama
from helpers.MessagesContainer import add_message, save_history
from Core.PromptGenerator import chat_prompt_Gen, system_prompt_Gen

# ------------------------
# init model
# ------------------------

MODEL_PATH = "./models/Qwen/qwen2.5-coder-7b-instruct-q5_k_m.gguf"
agent = Llama(
    model_path=MODEL_PATH,
    n_ctx=8192,
    n_threads=8,
    n_gpu_layers=28,
    temperature=0.0,
    verbose=False
)


def on_wake():   
     prompt = system_prompt_Gen()
     output = agent(
         prompt=prompt,
         max_tokens=128,
         stop=["<|im_end|>"]
     )
     reply = output["choices"][0]["text"].strip()
     print(reply)

def on_chat():
     try : 
          while True:
               user_input = input("ask anything : ").strip()
               if user_input.lower() in {"exit", "quit"}:
                    break
               add_message(role="user", content=user_input)
               prompt = chat_prompt_Gen()
               out = agent(
                    prompt= prompt,
                    max_tokens=512,
                    stop=["<|im_end|>"]
               )
               reply = out["choices"][0]["text"].strip()
               print("Sabrina : ", reply)
               add_message(role="Sabrina", content=reply)
     finally :
          add_message(role="system", content="User Left the Chat, Name this convo in 1 word for saving it")
          prompt = chat_prompt_Gen()
          out = agent(
               prompt= prompt,
               max_tokens=128,
               stop=["<|im_end|>"]
          )

on_wake()
on_chat()