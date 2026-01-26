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
from Tools.weather import get_weather

def SystemExecutions(fun:list):
      terminatation = False
      for fun in fun:
            value ,sep, key = fun.partition("(")
            match value:
                  case "terminatesession":
                        terminatation = True
                  case "weather":
                        
                        


                  
            
      return

def prompt_Analyzer(agent, input: str):
     """
     Analyze a user prompt and extract all matching tool calls with their
     corresponding parameters, if present.

     This function inspects the input query, determines which predefined
     tools (functions) are applicable, and returns their names along with
     any inferred arguments in a structured format.

     It is intended to be used as the decision layer for tool invocation,
     not for executing the tools themselves.

     :param agent: The LLM instance used to analyze and interpret the prompt.
     :type agent: Any

     :param input: Raw user input prompt to be analyzed.
     :type input: str

     :return: A list of detected tool calls with resolved arguments.
     :rtype: list
     """

     prompt = functional_prompt(f"User : {input}")
     print(prompt)
     out = agent(
                    prompt= prompt,
                    max_tokens=128,
                    temperature=0.1
               )
     reply = out["choices"][0]["text"]
     return reply

