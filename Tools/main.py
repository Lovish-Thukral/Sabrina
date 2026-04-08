"""
Model Toolset Integration queries your command for suitable actions.
Provides access to the following core capabilities:
* **Preferences:** User-specific settings and personalization.
* **Search:** Real-time web information retrieval.
* **Weather:** Current conditions and localized forecasts.
* **Learning:** Educational resources and knowledge expansion.
"""

import re
from Prompts.PromptProvider import functional_prompt
from Tools.weather import get_weather
from Tools.PrefrencesHandler import save_preference, preference_finder
from helpers.PromptConverter import array_Maker


def SystemExecutior(fun:list):
      """Executes parsed tool commands and returns system responses.

    Args:
        fun (list): List of command strings (e.g., "weather(Delhi,today)").

    Returns:
        dict: {
            "terminatation": bool,
            "System": str
        }"""
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
                        system += f"Save_Preference : \n system: {response}"
                  case "preference":
                        keywords = array_Maker(key)
                        data = preference_finder(keywords)
                        system += f"preference_finder: \n system:{data}"                  
      return {
            "terminate": terminatation,
            "System": system
      }

def Pre_Executor(agent, input: str):
    """
    Processes a user query, identifies required tool calls, executes them,
    and returns the results as system-level context for the AI agent.
    The resulting data is returned in a structured format to be consumed
    by the agent as contextual/system information for generating responses.
    :param agent: The LLM instance used to interpret the prompt and decide tool usage.
    :type agent: Any
    :param input: Raw user input prompt.
    :type input: str
    :return: Executed tool results formatted as system context.
    :rtype: dict
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
    

