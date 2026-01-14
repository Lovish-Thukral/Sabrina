# from getpass import getpass
# import subprocess
# import shlex

# password = getpass("Enter Your Password: ")
# command = "sudo -S apt-get install -y pycharm-community"
# splitcmnd = shlex.split(command)

# shell = subprocess.run(
#     splitcmnd,
#     input=password + "\n",
#     text=True,
#     capture_output=True
# )

# print(shell.stdout)
# print(shell.stderr)

from Core.CMND_Handler import Command_Executer

print(Command_Executer(Command="sudo -S apt-get install -y pycharm-community" ))