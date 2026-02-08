import subprocess
import shlex
from getpass import getpass
from helpers.MessagesContainer import HISTORY_CONTAINER
from Core.ReplyGenerator import shell_prompt_gen
# import pexpect


#-------------------------------------------------------------
# These Words Are Ignored for exectution for security reasons
#-------------------------------------------------------------
DangerousWords = {"-rf", "--no-preserve-root", "GRUB", "modprobe", "insmod", "rmmod", "lsmod", "iptables", "ip6tables", "nft", "ufw", "firewalld", "tc", "shutdown", "reboot", "poweroff", "halt", "init", "telinit", "systemctl", "mkfs", "mkfs.ext4", "mkfs.vfat", "fsck", "fsck.ext4", "mount", "umount", "dd", "wipefs", "blkdiscard", "parted", "fdisk", "cfdisk", "sfdisk", "losetup", "cryptsetup", "grub", "grub-install", "grub-mkconfig", "update-grub", "bios", "uefi", "efibootmgr", "bootctl", "shim", "fwupd", "fwupdmgr", "vim", "nano"}
DangerousCombinationsA = { "ip" }
DangerousCombinationsB = {"link", "route"}

def Command_Executer(Command: str, Dangerous = "yes"):
    """ Executes the Command via shell to the system; prop- { commands: command to execute, dangerous: yes/no} """

#-------------------------------------------------------------
# PARSE THE COMMAND FROM STRING TO SET TYPE FOR SAFE EXECUTION
#-------------------------------------------------------------
    if not Command:
        return {
            "Status" : "Blocked",
            "System" : "No Command Input Found"
        }
    try:
        cmnd = shlex.split(Command)
    except ValueError:
        return {
            "Status" : "Failed",
            "System" : "Unable to Parse Command in Shlex"
        }
    
    if not DangerousWords.isdisjoint(set(cmnd)):
        return {
            "Status" : "Blocked",
            "System" : "Execution is Blocked for Safty Purposes"
        }
    if not (DangerousCombinationsA.isdisjoint(set(cmnd))):
        if not (DangerousCombinationsB.isdisjoint(cmnd)):
            return {
            "Status" : "Blocked",
            "System" : "Execution is Blocked for Safty Purposes"
        } 
    
#-------------------------------------------------------------
# MAIN EXECUTION AND CAPUTRING AS TEXT 
#-------------------------------------------------------------
    try:
        if Dangerous.lower() == "yes" or "sudo" in cmnd:
                if "sudo" in cmnd and not "-S" in cmnd:
                    cmnd.remove("sudo")
                    cmnd.insert(0, "sudo")
                    cmnd.insert(1, "-S")

                password = getpass("Enter Your Password: ")
                shell = subprocess.run(
                    cmnd, 
                    input=password + "\n", 
                    text=True, 
                    capture_output=True,
                )
        else:
            shell = subprocess.run(cmnd, text=True, capture_output=True, check=True, timeout= 5)

        HISTORY_CONTAINER.append({"Shell:", shell})
        return{
            "Status" : "Success",
            "Shell"  : shell
        }
    except subprocess.TimeoutExpired as T:
        HISTORY_CONTAINER.append({"System" : "No Response Found from the Shell, Maybe a GUI Opening occured"})
        return{
            "Status" : "Success",
            "Shell" : "None \n System : Response Timeout, we cant see if the command is completed ask user"
        }
    except (ValueError, subprocess.CalledProcessError,
        FileNotFoundError,
        PermissionError,
        OSError) as e:
        error_str = str(e)
        HISTORY_CONTAINER.append(error_str)
        return {
            "Status": "Failed",
            "Error_Found": error_str
        }

def error_handler(agent, err:str):
    """
    Handles Retrial of Executions ( MAX 3 ATTEMPTS PREFFERED ) Upon Failed Executions    
    """
    error_found = f"Error_Found : {err}"
    r = 3
    while True:
        if r <= 0:
            return {
                "TTS" : "Looks like System Reached the Maximum Retrial Limit, You can Perform is Manually & I'll make through your way",
                "Status" : "Blocked"
            }
        temp = (4 - r) / 10
        New_Command = shell_prompt_gen(agent=agent, input=error_found, temp=temp)
        if New_Command["CMND"].lower() != "none" and New_Command.get("ispossible", "").lower() == "yes":
            HISTORY_CONTAINER.append(New_Command)
            error_found += f"\n Sabrina : {New_Command["CMND"]}"
            x = input("Are You Sure ?")
            if(x.lower() == "yes"):
                r -= 1
                shell = Command_Executer(Command=New_Command["CMND"], Dangerous=New_Command["DANGER"])
                if (shell["Status"] == "Success" or shell["Status"] == "Blocked") :
                    return shell
                else:
                    new_err = shell["Error_Found"] or ""
                    HISTORY_CONTAINER.append({f"Shell: {new_err}"})
                    error_found += f"\n Error_found: {new_err}"
                    continue
            else:
                return {
                    "Status" : "Blocked",
                    "TTS" : "Okay, I'll Stop Execution, Anything Else?"
                }
        else:
            HISTORY_CONTAINER.append(New_Command)
            return{
                "TTS" : New_Command["TTS"],
                "Status" : "Blocked"
            }
        