"""
Model Toolset Integration queries your command for suitable actions.
Provides access to the following core capabilities:
* **Preferences:** User-specific settings and personalization.
* **Search:** Real-time web information retrieval.
* **Weather:** Current conditions and localized forecasts.
* **Current Time:** Temporal synchronization and date/time data.
* **Learning:** Educational resources and knowledge expansion.
"""

def chat_prompt_gen(agent, input: str):
     prompt = input
     out = agent(
                    prompt= prompt,
                    max_tokens=512,
                    stop=["<|im_end|>"],
                    temperature=0.3
               )
     reply = out["choices"][0]["text"]
     return response

# add functional prompt and further query for mini llm