"""
Model Toolset Integration queries your command for suitable actions.
Provides access to the following core capabilities:
* **Preferences:** User-specific settings and personalization.
* **Search:** Real-time web information retrieval.
* **Weather:** Current conditions and localized forecasts.
* **Current Time:** Temporal synchronization and date/time data.
* **Learning:** Educational resources and knowledge expansion.
"""

from SystemPrompts.PromptProvider import functional_prompt
def prompt_Analyzer(agent, input: str):
     prompt = functional_prompt(f"User : {input}")
     print(prompt)
     out = agent(
                    prompt= prompt,
                    max_tokens=128,
                    temperature=0.1
               )
     reply = out["choices"][0]["text"]
     return reply

# add functional prompt and further query for mini llm