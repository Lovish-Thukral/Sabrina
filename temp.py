import subprocess

x = subprocess.run("firefox", capture_output=True, text=True)

print(x)