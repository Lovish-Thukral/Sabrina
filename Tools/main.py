"""
Model Toolset Integration queries your command for suitable actions.
Provides access to the following core capabilities:
* **Preferences:** User-specific settings and personalization.
* **Search:** Real-time web information retrieval.
* **Weather:** Current conditions and localized forecasts.
* **Learning:** Educational resources and knowledge expansion.
"""

import re
from SystemPrompts.PromptProvider import functional_prompt
from Tools.weather import get_weather
from Tools.PrefrencesHandler import save_preference, preference_finder
from helpers.PromptConverter import array_Maker

def SystemExecutior(fun:list):
      terminatation = False
      system = ""
      for f in fun:
            string = f.strip()
            value ,_, key = string.partition("(")
            key = key.replace(" ", "")
            key = key.strip(")")
            match value.lower():
                  case "terminatesession":
                        terminatation = True
                  case "weather":
                        city, _ , date = key.partition(",")
                        print(city, "im", date)
                        terminatation = False
                        if re.fullmatch(r"[A-Za-z]+", city) and "/" in date:
                            print(city, date)
                            data = get_weather(city=city, d=date.strip())
                            system += f"{value}: {data} "
                        elif re.fullmatch(r"[A-Za-z]+", date) and "/" in city:
                            data = get_weather(city=date, d=city)
                            system += f"{value}: {data} "
                        elif date.lower() in ["today", "yesterday", "tomorrow"]:
                            data = get_weather(city=city, d=date)
                            system += f"{value}: {data} "
                        elif city.lower() in ["today", "yesterday", "tomorrow"]:
                            data = get_weather(city=date, d=city)
                            system += f"{value}: {data} "
                        else:
                            system += f"Improper Values Detected for {value} API, Cannot Fetch at the moment"
                  case "save_preference":
                        name, _ , val = key.partition(",")
                        response = save_preference(name, val)
                        system += f"Save_Prefrence : \n system: {response}"
                  case "prefrence":
                        keywords = array_Maker(key)
                        data = preference_finder(keywords)
                        system += f"prefrence_finder: \n system:{data}"                  
      return {
            "terminatation": terminatation,
            "System": system
      }

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
     out = agent(
                    prompt= prompt,
                    max_tokens=128,
                    temperature=0.1
               )
     reply = out["choices"][0]["text"]
     commands = array_Maker(reply)
     return SystemExecutior(commands)
    