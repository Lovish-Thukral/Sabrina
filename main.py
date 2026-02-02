from llama_cpp import Llama
from helpers.MessagesContainer import save_history
from Core.ReplyGenerator import chat_prompt_gen, system_promp_gen
from Core.CMND_Handler import Command_Executer, error_handler
from helpers.MessagesContainer import HISTORY_CONTAINER
from Tools.main import prompt_Analyzer
from helpers.Screen_Operation import get_current_screen

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

def main_loop():
      res = system_promp_gen(agent=agent, isboot=True)
      print(res)
      while True:
            userInput = input("User : ").strip()
            System = prompt_Analyzer(agent=agent, input=userInput)
            print(System)
            if System["terminatation"] == True:
                  response = chat_prompt_gen(agent=agent, input=userInput)
                  print(response)
                  x = chat_prompt_gen(agent=agent, input=" \n System :Name This Entire session with one word to save it")
                  print(x)
                  name = x["TTS"]["Speech"]
                  save_history(name)
                  break
            query = f"Currunt Screen: {get_current_screen()} \n User: {userInput} \n {System}"
            reply = chat_prompt_gen(agent=agent, input=query)
            print(reply)
            if(reply.get("CMND", "").lower() != "none"):
                    CMND_response = Command_Executer(Command=reply.get("CMND"), Dangerous=reply.get("DANGER"))
                    print(CMND_response)
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
                         err = f"{query} \n Command: {reply.get("CMND")} \n Error_Found: {CMND_response["Error_Found"]}"
                         debug =  error_handler(agent=agent, err=err)
                         Error_Status = debug["Status"]
                         if Error_Status == "Blocked":
                              print(debug.get("TTS", "The Command Exceeds the System policies, i can't execute the retrial"))
                              continue
                         if Error_Status == "Success":
                               x = chat_prompt_gen(agent=agent, input=f"System: Execution Success, ask next action \n Shell: {debug["Shell"]}")
                               continue

main_loop()