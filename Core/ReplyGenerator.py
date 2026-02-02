from SystemPrompts.PromptProvider import chat_prompt, shell_prompt
from helpers.MessagesContainer import add_message
from SystemPrompts.PromptProvider import system_prompt
from helpers.PromptConverter import JSON_maker

def chat_prompt_gen(agent, input: str):
     add_message(role="user", content=input)
     prompt = chat_prompt()
     out = agent(
                    prompt= prompt,
                    max_tokens=512,
                    stop=["<|im_end|>"],
                    temperature=0.3
               )
     reply = out["choices"][0]["text"]
     add_message(role="Sabrina", content=reply.strip())
     response = JSON_maker(reply)
     return response

def system_promp_gen(agent, isboot = False):
     prompt = system_prompt(isboot)
     output = agent(
         prompt=prompt,
         max_tokens=128,
         stop=["<|im_end|>"],
         temperature=0.9
     )
     reply = output["choices"][0]["text"].strip()
     response = JSON_maker(reply)
     return response

def shell_prompt_gen(agent, input: str, temp = 0.1, tokens = 1024):
    try:
        prompt = shell_prompt(input)        
        print(f"DEBUG: Prompt sent to LLM (last 500 chars): {input}")        
        output = agent(
            prompt=prompt,
            max_tokens=tokens,
            temperature=temp,
            stop=["} \n }"],   # stop after JSON closes
        )
        
        reply = output["choices"][0]["text"]
        print(f"DEBUG: Raw LLM response:\n{reply}")
        
        response = JSON_maker(reply)
        
        if response is None:
            print("WARNING: JSON_maker returned None")
            response = {
                "ispossible": "no",
                "CMND": "none",
                "TTS": "System error in response generation",
                "DANGER": "NO",
                "ERROR": "JSON_maker_NONE"
            }
        
        print(f"DEBUG: Parsed response: {response}")
        return response
        
    except Exception as e:
        print(f"EXCEPTION in shell_prompt_gen: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "ispossible": "no",
            "CMND": "none",
            "TTS": f"System error: {str(e)[:50]}",
            "DANGER": "NO",
            "ERROR": "EXCEPTION"
        }