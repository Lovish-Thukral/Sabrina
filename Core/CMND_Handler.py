import subprocess
import shlex
import os
import tempfile
import stat
from helpers.MessagesContainer import HISTORY_CONTAINER
from Core.ReplyGenerator import shell_prompt_gen

ALLOWED_SUDO_TOOLS = frozenset({
    "apt", "apt-get", "apt-cache",
    "snap", "flatpak",
    "dnf", "yum",
    "pacman", "zypper",
    "pip", "pip3",
    "npm", "yarn", "pnpm",
    "gem", "cargo",
})

ALLOWED_PKG_SUBCMDS = frozenset({
    "install", "add",
    "update", "upgrade", "dist-upgrade", "full-upgrade", "refresh",
    "remove", "uninstall", "purge", "autoremove", "autoclean", "clean",
    "list", "search", "show", "info", "depends", "rdepends",
})

ALWAYS_BLOCKED = frozenset({
    "-rf", "--no-preserve-root", "dd", "wipefs", "blkdiscard",
    "mkfs", "mkfs.ext4", "mkfs.vfat", "fsck", "fsck.ext4",
    "parted", "fdisk", "cfdisk", "sfdisk", "losetup",
    "grub", "grub-install", "grub-mkconfig", "update-grub",
    "efibootmgr", "bootctl", "shim", "fwupd", "fwupdmgr",
    "modprobe", "insmod", "rmmod", "lsmod",
    "iptables", "ip6tables", "nft", "ufw", "firewalld", "tc",
    "shutdown", "reboot", "poweroff", "halt", "init", "telinit",
    "mount", "umount", "cryptsetup",
    "su", "passwd", "chpasswd", "visudo", "usermod", "useradd",
    "userdel", "groupadd", "groupdel", "chown", "chmod",
    "vim", "nano", "vi", "emacs", "gedit", "kate",
    "curl", "wget",
    "bash", "sh", "zsh", "fish", "python", "python3",
    "GRUB", "systemctl",
})

# ── askpass helpers, tried in order ──────────────────────────────────────────
_ASKPASS_CANDIDATES = [
    "/usr/bin/ssh-askpass",
    "/usr/lib/ssh/ssh-askpass",
    "/usr/lib/openssh/gnome-ssh-askpass",
    "/usr/bin/ksshaskpass",
    "/usr/lib/seahorse/seahorse-ssh-askpass",
    "/usr/libexec/openssh/gnome-ssh-askpass",
    "/usr/bin/git-gui--askpass",
    "/usr/lib/git-core/git-gui--askpass",
]


def _result(status: str, response: str) -> dict:
    return {"Status": status, "Response": response}


def _parse(command: str):
    try:
        tokens = shlex.split(command)
        return tokens if tokens else None
    except ValueError:
        return None


def _extract_output(proc: subprocess.CompletedProcess) -> str:
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    if stdout:
        return stdout
    if stderr:
        return stderr
    return f"Command exited with code {proc.returncode} and produced no output."


def _extract_error(proc: subprocess.CompletedProcess) -> str:
    parts = [f"Command failed (exit code {proc.returncode})."]
    stderr = (proc.stderr or "").strip()
    stdout = (proc.stdout or "").strip()
    if stderr:
        parts.append(f"stderr:\n{stderr}")
    if stdout:
        parts.append(f"stdout:\n{stdout}")
    return "\n".join(parts)


def _validate_sudo_command(tokens: list) -> tuple[bool, str]:
    rest = [t for t in tokens if t != "sudo"]
    if not rest:
        return False, "No command found after sudo."
    tool = rest[0].lower()
    if tool not in ALLOWED_SUDO_TOOLS:
        return False, (
            f"sudo is only permitted with package managers "
            f"({', '.join(sorted(ALLOWED_SUDO_TOOLS))}). "
            f"'{tool}' is not allowed."
        )
    if len(rest) < 2:
        return False, f"No sub-command given to '{tool}'."
    subcmd = rest[1].lower().lstrip("-")
    if subcmd not in ALLOWED_PKG_SUBCMDS:
        return False, (
            f"'{subcmd}' is not an allowed sub-command for sudo. "
            "Only package install / update / remove operations are permitted."
        )
    return True, "OK"


def _find_askpass() -> str | None:
    """Return the first available askpass binary, or None."""
    for path in _ASKPASS_CANDIDATES:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def _make_zenity_askpass() -> str:
    """
    Write a tiny shell script that uses zenity (GTK dialog) as askpass,
    save it to a temp file, make it executable, and return its path.
    This is used when no system askpass binary is found.
    Caller is responsible for deleting the file after use.
    """
    script = (
        "#!/bin/sh\n"
        'zenity --password --title="Authentication Required" '
        '--text="Enter your password to continue:" 2>/dev/null\n'
    )
    fd, path = tempfile.mkstemp(prefix="sabrina_askpass_", suffix=".sh")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(script)
        os.chmod(path, stat.S_IRWXU)  # 0o700 — owner only
    except Exception:
        os.unlink(path)
        raise
    return path


def _run_with_sudo_askpass(tokens: list, timeout: int = 60) -> tuple[subprocess.CompletedProcess, str | None]:
    """
    Run an elevated command using sudo -A (askpass mode).
    sudo -A reads SUDO_ASKPASS and launches it to prompt for a password,
    which works from any GUI session including browser-based terminals.

    Returns (CompletedProcess, temp_askpass_path_or_None).
    The caller must delete the temp file if one was created.
    """
    # Strip leading 'sudo' — we re-add it ourselves
    cmd_tokens = [t for t in tokens if t != "sudo"]

    askpass = _find_askpass()
    temp_file = None

    if askpass is None:
        # Try building a zenity-based askpass on the fly
        try:
            askpass = _make_zenity_askpass()
            temp_file = askpass
        except Exception:
            askpass = None  # will fail gracefully below

    if askpass is None:
        raise FileNotFoundError(
            "No askpass helper found. Install one with: "
            "sudo apt install ssh-askpass   # or   sudo apt install zenity"
        )

    env = os.environ.copy()
    env["SUDO_ASKPASS"] = askpass
    # Ensure a display is set so the GUI dialog can open
    env.setdefault("DISPLAY", ":0")
    env.setdefault("DBUS_SESSION_BUS_ADDRESS", os.environ.get("DBUS_SESSION_BUS_ADDRESS", ""))

    proc = subprocess.run(
        ["sudo", "-A"] + cmd_tokens,
        text=True,
        capture_output=True,
        timeout=timeout,
        env=env,
    )
    return proc, temp_file


def Command_Executer(Command: str) -> dict:
    if not Command or not Command.strip():
        return _result("Blocked", "No command input was provided.")

    tokens = _parse(Command)
    if tokens is None:
        return _result("Failed", "Command could not be parsed by shlex. Check for unmatched quotes or invalid syntax.")
    if not tokens:
        return _result("Blocked", "Command resolved to an empty token list after parsing.")

    token_set = frozenset(t.lower() for t in tokens)

    blocked_hits = ALWAYS_BLOCKED & token_set
    if blocked_hits:
        return _result(
            "Blocked",
            f"Command contains permanently blocked token(s): {sorted(blocked_hits)}. "
            "Execution refused for safety."
        )

    uses_sudo = "sudo" in token_set

    # ── sudo path ─────────────────────────────────────────────────────────────
    if uses_sudo:
        allowed, reason = _validate_sudo_command(tokens)
        if not allowed:
            return _result("Blocked", f"Sudo command rejected — {reason}")

        temp_file = None
        try:
            proc, temp_file = _run_with_sudo_askpass(tokens, timeout=60)
        except FileNotFoundError as e:
            return _result("Failed", str(e))
        except subprocess.TimeoutExpired:
            return _result(
                "Success",
                "Command timed out after 60 seconds. It may still be running in the background."
            )
        except (ValueError, PermissionError, OSError) as e:
            return _result("Failed", str(e))
        finally:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)

        if proc.returncode == 0:
            return _result("Success", _extract_output(proc))
        return _result("Failed", _extract_error(proc))

    # ── non-sudo path ─────────────────────────────────────────────────────────
    try:
        proc = subprocess.run(tokens, text=True, capture_output=True, timeout=5)
    except subprocess.TimeoutExpired:
        return _result(
            "Success",
            "Command timed out after 5 seconds. if its an app opening its opened, if something else, its running in the background."
        )
    except FileNotFoundError:
        return _result("Failed", f"Command not found: '{tokens[0]}'. Is it installed and on PATH?")
    except (ValueError, PermissionError, OSError) as e:
        return _result("Failed", str(e))

    if proc.returncode == 0:
        return _result("Success", _extract_output(proc))
    return _result("Failed", _extract_error(proc))


def error_handler(agent, err: str, STT, TTS) -> dict:
    if not err or not err.strip():
        return _result("Blocked", "No error input provided to handler.")

    error_log = f"Error:\n{err}"

    for attempt in range(3):
        temp = (attempt + 1) / 10
        new_cmd = shell_prompt_gen(agent=agent, input=error_log, temp=temp)
        cmd_str  = new_cmd.get("CMND", "").strip()
        possible = new_cmd.get("ispossible", "").lower()
        tts_str  = new_cmd.get("TTS", "")
        danger   = new_cmd.get("DANGER", "no").lower()
        HISTORY_CONTAINER.append(new_cmd)
        if not cmd_str or cmd_str.lower() == "none" or possible != "yes":
            return _result("Blocked", tts_str)
        if danger == "yes":
            TTS.play(tts_str)
            TTS.play(
                text="Needs Your Confirmation, The Command Seems Dangerous. Say yes, if you want to proceed?",
            )
            user_response = STT.listen()
            if "yes" not in user_response.lower():
                TTS.play("Okay, stopping execution.")
                HISTORY_CONTAINER.append({"Blocked": "User declined dangerous command."})
                return _result("Blocked", "User declined dangerous command.")
        shell = Command_Executer(Command=cmd_str)
        response_text = shell["Response"] if isinstance(shell["Response"], str) else str(shell["Response"])
        HISTORY_CONTAINER.append({"Attempt": attempt + 1, "Command": cmd_str, "Result": response_text})

        if shell["Status"] == "Success":
            return _result("Success", response_text)
        if shell["Status"] == "Blocked":
            return _result("Blocked", response_text)

        error_log += f"\nAttempt {attempt + 1} ran: {cmd_str}\nResult:\n{response_text}"

    return _result(
        "Blocked",
        "Maximum retry limit reached. You can perform the task manually and I will guide you through it."
    )