from SystemPrompts.PromptProvider import chat_prompt
from helpers.MessagesContainer import add_message
from SystemPrompts.PromptProvider import system_prompt

def chat_prompt_InOut(agent, temperature: float, input: str) -> str:
     add_message(role="user", content=input)
     prompt = chat_prompt()
     out = agent(
                    prompt= prompt,
                    max_tokens=512,
                    stop=["<|im_end|>"],
                    temperature=temperature
               )
     reply = out["choices"][0]["text"]
     add_message(role="Sabrina", content=reply.strip())
     return reply

def system_promp_gen(agent, isboot = False) -> str:
     prompt = system_prompt(isboot)
     output = agent(
         prompt=prompt,
         max_tokens=128,
         stop=["<|im_end|>"],
         temperature=0.9
     )
     reply = output["choices"][0]["text"].strip()
     return reply