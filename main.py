from llama_cpp import Llama
from helpers.MessagesContainer import save_history
from Core.PromptGenerator import chat_prompt_gen, system_promp_gen
from Core.CMND_Handler import Command_Executer, error_handler
from helpers.MessagesContainer import HISTORY_CONTAINER

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

res = system_promp_gen(agent=agent, isboot=True)
print(res)

def on_chat():
          while True:
               user_input = input("ask anything : ").strip()
               # ------------------------
               # if user type exit, it'll leave the session and save the history
               # ------------------------
               if user_input.lower() in {"exit", "quit"}:
                    reply = chat_prompt_gen(agent=agent, input="User Left the Chat, Name this convo in 1 word for saving it")
                    save_history(reply)
                    break

               reply = chat_prompt_gen(agent=agent, input=user_input)
               print(reply)
               if(reply.get("CMND", "").lower() != "none"):
                    CMND_response = Command_Executer(Command=reply.get("CMND"), Dangerous=reply.get("DANGER"))
                    status = CMND_response["Status"]
                    if status == "Blocked":
                          HISTORY_CONTAINER.append(f"Blocked: {CMND_response["System"]}")
                          x = chat_prompt_gen(agent=agent, input=CMND_response["System"])
                          print(x)
                          continue
                    if status == "Success":
                          x = chat_prompt_gen(agent=agent, input=f"System: ask user next action as per resoponse \n Shell: {CMND_response["Shell"]}")
                          print (x)
                          continue
                    if status == "Failed":
                         debug =  error_handler(agent=agent, err=CMND_response["Error_Found"])
                         Error_Status = debug["Status"]
                         if Error_Status == "Blocked":
                              print(debug.get("TTS", "The Command Exceeds the System policies, i can't execute the retrial"))
                              continue
                         if Error_Status == "Success":
                               x = chat_prompt_gen(agent=agent, input=f"System: Execution Success, ask next action \n Shell: {debug["Shell"]}")
                               continue
                               

on_chat()


