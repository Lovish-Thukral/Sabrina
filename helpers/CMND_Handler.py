import json
import subprocess
import shlex

#-------------------------------------------------------------
# These Words Are Ignored for exectution for security reasons
#-------------------------------------------------------------

DangerousWords = {"-rf", "--no-preserve-root", "GRUB", "modprobe", "insmod", "rmmod", "lsmod", "iptables", "ip6tables", "nft", "ufw", "firewalld", "tc", "ip link", "ip route", "shutdown", "reboot", "poweroff", "halt", "init", "telinit", "systemctl poweroff", "systemctl reboot", "mkfs", "mkfs.ext4", "mkfs.vfat", "fsck", "fsck.ext4", "mount", "umount", "dd", "wipefs", "blkdiscard", "parted", "fdisk", "cfdisk", "sfdisk", "losetup", "cryptsetup", "grub", "grub-install", "grub-mkconfig", "update-grub", "bios", "uefi", "efibootmgr", "bootctl", "shim", "fwupd", "fwupdmgr"}


def JSON_maker(reply: str):
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


def CMND_Valid(reply: str):
    data = JSON_maker(reply)
    command = data.get("CMND", "")
    danger = data.get("DANGER", "").lower()
    
    try:
        parts = shlex.split(command)
    except ValueError:
        print("Invalid command format")
        return False

    if (flag in parts for flag in DangerousWords):
        return "Command Provided is Blocked by the system, report user the about the same"
    elif (danger == "yes" and "sudo" in parts):
        #add tts for dangerous flag and password input
        password = input("enter password for this command")

#---------------------------------------------------------------
# TEXT IS TRUE SO THAT WE'LL GET STR OUTPUT NOT BINARY
#---------------------------------------------------------------
        usershell = subprocess.run(command, input=password + "/n", text=True, capture_output=True)
        return usershell.split()
        

