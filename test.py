import json
"Decides which model to Load based on the System Configuration, and Returns the Model Path and Repository Information"
with open("UserPreferences/userMetaData.json", "r") as f:
    data = json.load(f)
user = data.get("user", {})
if not user:
    raise ValueError("User information not found in UserMetaData.json, re-execute the install.sh. Don't Worry Nothing gonna download again")
gpu = user.get("vram", "N/A" )
print(gpu)