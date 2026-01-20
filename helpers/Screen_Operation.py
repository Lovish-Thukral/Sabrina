import subprocess

def get_current_screen():
    out = subprocess.run(
        ["xdotool", "getactivewindow", "getwindowname"],
        capture_output=True,
        text=True,
        check=False
    )
    return out.stdout.strip()


