import json
import re
def JSON_maker(reply: str) -> dict:
   """
   Returns JSON FOR of provided string
   :type reply: str
   :rtype: dict
   """
   try:
       # Find the start and end of the JSON object
       start = reply.find('{')
       end = reply.rfind('}') + 1
       
       if start == -1 or end == 0:
           raise ValueError("No JSON object found in the response")
           
       json_str = reply[start:end]
       jsonData = json.loads(json_str)
       return jsonData
       
   except (json.JSONDecodeError, ValueError) as e:
       print(f"Failed to parse JSON: {e}")

def array_Maker(array: str):
    match = re.search(r'\[(.*)\]', array)
    if not match:
        return None

    content = match.group(1)

    # split only commas not inside parentheses
    items = re.split(r',\s*(?![^()]*\))', content)
    return [item.strip() for item in items]