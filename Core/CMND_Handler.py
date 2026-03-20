import subprocess
import shlex
from helpers.MessagesContainer import HISTORY_CONTAINER
from Core.ReplyGenerator import shell_prompt_gen

DANGEROUS_WORDS = frozenset({
    "-rf", "--no-preserve-root", "GRUB", "modprobe", "insmod", "rmmod", "lsmod",
    "iptables", "ip6tables", "nft", "ufw", "firewalld", "tc", "shutdown", "reboot",
    "poweroff", "halt", "init", "telinit", "systemctl", "mkfs", "mkfs.ext4",
    "mkfs.vfat", "fsck", "fsck.ext4", "mount", "umount", "dd", "wipefs",
    "blkdiscard", "parted", "fdisk", "cfdisk", "sfdisk", "losetup", "cryptsetup",
    "grub", "grub-install", "grub-mkconfig", "update-grub", "bios", "uefi",
    "efibootmgr", "bootctl", "shim", "fwupd", "fwupdmgr", "vim", "nano"
})
DANGEROUS_COMBO_A = frozenset({"ip"})
DANGEROUS_COMBO_B = frozenset({"link", "route"})

def _result(status: str, response) -> dict:
    return {"Status": status, "Response": response}

def _is_dangerous(token_set: frozenset) -> bool:
    if not DANGEROUS_WORDS.isdisjoint(token_set):
        return True
    if not DANGEROUS_COMBO_A.isdisjoint(token_set) and not DANGEROUS_COMBO_B.isdisjoint(token_set):
        return True
    return False


def Command_Executer(Command: str) -> dict:
    """Executes a shell command as root. Returns { Status, Response }."""

    if not Command or not Command.strip():
        return _result("Blocked", "No Command Input Found")

    try:
        cmnd = shlex.split(Command)
    except ValueError:
        return _result("Failed", "Unable to Parse Command in Shlex")

    if not cmnd:
        return _result("Blocked", "Command Parsed to Empty Token List")

    if _is_dangerous(frozenset(cmnd)):
        return _result("Blocked", "Execution is Blocked for Safety Purposes")

    try:
        shell = subprocess.run(cmnd, text=True, capture_output=True, timeout=5)
        return _result("Success", shell)
    except subprocess.TimeoutExpired:
        return _result("Success", "Response Timeout — command may still be running, ask user")
    except (ValueError, FileNotFoundError, PermissionError, OSError) as e:
        return _result("Failed", str(e))

def error_handler(agent, err: str, STT, TTS) -> dict:
    """Retries failed executions up to 3 times. Returns { Status, Response }."""

    if not err or not err.strip():
        return _result("Blocked", "No Error Input Provided to Handler")

    error_log = f"Error_Found: {err}"

    for attempt in range(3):
        temp = (attempt + 1) / 10
        new_cmd = shell_prompt_gen(agent=agent, input=error_log, temp=temp)

        cmd_str  = new_cmd.get("CMND", "").lower()
        possible = new_cmd.get("ispossible", "").lower()
        tts_str  = new_cmd.get("TTS", "")
        danger   = new_cmd.get("DANGER", "no").lower()

        if cmd_str == "none" or possible != "yes":
            HISTORY_CONTAINER.append(new_cmd)
            TTS.play(tts_str)
            return _result("Blocked", tts_str)

        if danger == "yes":
            TTS.play(tts_str)
            TTS.play(text = "The Command is Dangerous, Just Say Yes if you want to execute", cloningchar = "Nitin")
            user_response = STT.listen()
            if "yes" not in user_response.lower():
                TTS.play("Okay, Stopping Execution.")
                return _result("Blocked", "User Declined Dangerous Command")

        HISTORY_CONTAINER.append(new_cmd)
        error_log += f"\nSabrina: {new_cmd['CMND']}"

        shell = Command_Executer(Command=new_cmd["CMND"])

        if shell["Status"] in ("Success", "Blocked"):
            return shell

        new_err = shell["Response"] if isinstance(shell["Response"], str) else str(shell["Response"])
        HISTORY_CONTAINER.append({f"Shell: {new_err}"})
        error_log += f"\nError_Found: {new_err}"

    return _result("Blocked", "Reached Maximum Retrial Limit, You can Perform it Manually & I'll guide you through")
    
    