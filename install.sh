#!/bin/bash

set -e

echo "🔧 Starting Sabrina AI setup..."

# -----------------------------
# Detect Platform
# -----------------------------
OS="$(uname -s 2>/dev/null || echo "Windows")"

case "$OS" in
    Linux*)   PLATFORM="linux" ;;
    MINGW*|MSYS*|CYGWIN*) PLATFORM="windows" ;;
    *)
        if [ -n "$WINDIR" ] || [ -n "$COMSPEC" ]; then
            PLATFORM="windows"
        else
            PLATFORM="linux"
        fi
        ;;
esac

echo "🖥️  Detected platform: $PLATFORM"

# -----------------------------
# Detect Python
# -----------------------------
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo "❌ Python not found. Please install Python 3.10+ and try again."
    exit 1
fi

echo "🐍 Using Python: $($PYTHON --version)"

# -----------------------------
# Create Virtual Environment
# -----------------------------
VENV_DIR=".venv"

if [ -d "$VENV_DIR" ]; then
    echo "✅ Virtual environment already exists at $VENV_DIR"
else
    echo "🌀 Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
    echo "✅ Virtual environment created at $VENV_DIR"
fi

# Activate venv and set pip path
if [ "$PLATFORM" == "windows" ]; then
    PIP="$VENV_DIR/Scripts/pip"
    PYTHON="$VENV_DIR/Scripts/python"
else
    PIP="$VENV_DIR/bin/pip"
    PYTHON="$VENV_DIR/bin/python"
fi

# Upgrade pip silently
"$PIP" install --upgrade pip --quiet

# -----------------------------
# Install System Audio Dependencies (Linux only)
# -----------------------------
if [ "$PLATFORM" == "linux" ]; then
    echo "🎙️  Installing PortAudio system dependencies..."
    sudo apt install -y portaudio19-dev python3-pyaudio xdotool
fi

# -----------------------------
# Install Python dependencies
# -----------------------------
echo "📦 Installing Python requirements..."
"$PIP" install -r requirements.txt

# -----------------------------
# GPU Selection
# -----------------------------
echo ""
read -p "💻 Do you have an NVIDIA GPU? (y/n): " gpu_choice
gpu_choice=${gpu_choice:-n}

if [[ "$gpu_choice" =~ ^[Yy]$ ]]; then

    # -----------------------------
    # Check CUDA Toolkit
    # -----------------------------
    if ! command -v nvcc &>/dev/null; then
        echo ""
        echo "⚠️  NVIDIA CUDA Toolkit not found on your system."
        echo "    llama-cpp-python requires CUDA to be installed before continuing."
        echo ""

        if [ "$PLATFORM" == "windows" ]; then
            echo "    👉 Download and install CUDA Toolkit for Windows:"
            echo "       https://developer.nvidia.com/cuda-downloads"
            echo ""
            echo "    After installing, re-run this setup script."
        else
            echo "    Choose an option:"
            echo "    [1] Install CUDA Toolkit now  (sudo apt install nvidia-cuda-toolkit)"
            echo "    [2] Open download page        (https://developer.nvidia.com/cuda-downloads)"
            echo ""
            read -p "    Enter choice (1/2): " cuda_choice
            cuda_choice=${cuda_choice:-1}

            if [[ "$cuda_choice" == "1" ]]; then
                echo "⬇️  Installing NVIDIA CUDA Toolkit..."
                sudo apt install -y nvidia-cuda-toolkit
                echo "✅ CUDA Toolkit installed."
            else
                echo ""
                echo "    👉 Visit: https://developer.nvidia.com/cuda-downloads"
                echo "    After installing CUDA, re-run this setup script."
                exit 0
            fi
        fi

        # Verify CUDA is now available
        if ! command -v nvcc &>/dev/null; then
            echo ""
            echo "❌ CUDA still not detected. Please install it and re-run setup."
            exit 1
        fi
    fi

    echo "⚡ Installing llama-cpp-python with CUDA..."
    CMAKE_ARGS="-DGGML_CUDA=on" GGML_CCACHE=OFF "$PIP" install llama-cpp-python

else
    echo "🐢 Installing llama-cpp-python (CPU)..."
    "$PIP" install llama-cpp-python
fi

# -----------------------------
# Install PyTorch (CPU only)
# -----------------------------
echo "🔥 Installing PyTorch (CPU)..."
"$PIP" install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# -----------------------------
# Install Neutts
# -----------------------------
echo "🔊 Installing Neutts..."
"$PIP" install "neutts[llama]"
"$PIP" install "neutts[onnx]"

# -----------------------------
# Collect User Info
# -----------------------------
echo ""
read -p "👤 Enter your name: " user_name
user_name=${user_name:-"User"}

read -p "⚧  Enter your gender (Male/Female/Other): " user_gender
user_gender=${user_gender:-"Other"}

# Detect OS pretty name
if [ -f /etc/os-release ]; then
    user_os=$(. /etc/os-release && echo "$PRETTY_NAME")
elif [ "$PLATFORM" == "windows" ]; then
    user_os="Windows"
else
    user_os=$(uname -s)
fi

# Detect default shell
if [ "$PLATFORM" == "windows" ]; then
    default_shell="cmd"
    [ -n "$PSModulePath" ] && default_shell="powershell"
else
    default_shell=$(basename "$SHELL")
fi

# -----------------------------
# Detect Total RAM
# -----------------------------
if [ "$PLATFORM" == "linux" ]; then
    total_ram_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    total_ram_mb=$((total_ram_kb / 1024))
    total_ram="${total_ram_mb}"
elif [ "$PLATFORM" == "windows" ]; then
    total_ram_bytes=$(wmic ComputerSystem get TotalPhysicalMemory /value 2>/dev/null | grep = | cut -d= -f2 | tr -d '\r')
    if [ -n "$total_ram_bytes" ]; then
        total_ram_mb=$((total_ram_bytes / 1024 / 1024))
        total_ram="${total_ram_mb}"
    else
        total_ram="Unknown"
    fi
else
    total_ram="Unknown"
fi

# -----------------------------
# Detect VRAM (if GPU selected)
# -----------------------------
vram="N/A"
if [[ "$gpu_choice" =~ ^[Yy]$ ]]; then
    if command -v nvidia-smi &>/dev/null; then
        vram_mb=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -n1 | tr -d ' ')
        if [ -n "$vram_mb" ]; then
            vram="${vram_mb}"
        else
            vram="Unknown"
        fi
    else
        vram="Unknown"
    fi
fi

# -----------------------------
# Create User Metadata
# -----------------------------
METADATA_DIR="UserPreferences"
METADATA_FILE="${METADATA_DIR}/userMetaData.json"

mkdir -p "$METADATA_DIR"

cat > "$METADATA_FILE" <<METAEOF
{
    "version": "1.0",
    "user": {
        "name": "${user_name}",
        "gender": "${user_gender}",
        "user_os": "${user_os}",
        "default_shell": "${default_shell}",
        "total_ram": "${total_ram}",
        "vram": "${vram}"
    },
    "preferences": {}
}
METAEOF

echo "✅ User metadata saved to $METADATA_FILE"

# -----------------------------
# Launch Sabrina AI
# -----------------------------
echo ""
echo "🚀 Setup complete! Launching Sabrina AI..."
echo ""

CURRENT_DIR="$(pwd)"

if [ "$PLATFORM" == "windows" ]; then

    # -----------------------------
    # Create Desktop Shortcut (Windows)
    # -----------------------------
    echo "🖥️  Creating desktop shortcut..."

    BAT_FILE="$(cygpath -w "$CURRENT_DIR/shortcutkey.bat" 2>/dev/null || echo "$CURRENT_DIR\\shortcutkey.bat")"
    DESKTOP="$(cygpath "$USERPROFILE/Desktop" 2>/dev/null || echo "$USERPROFILE\\Desktop")"
    LINK_FILE="$DESKTOP\\Sabrina.lnk"
    VBS_FILE="$CURRENT_DIR\\create_shortcut.vbs"

    # Prefer .ico, fall back to .png
    if [ -f "$CURRENT_DIR/icon.ico" ]; then
        ICO_FILE="$(cygpath -w "$CURRENT_DIR/icon.ico" 2>/dev/null || echo "$CURRENT_DIR\\icon.ico")"
    elif [ -f "$CURRENT_DIR/icon.png" ]; then
        ICO_FILE="$(cygpath -w "$CURRENT_DIR/icon.png" 2>/dev/null || echo "$CURRENT_DIR\\icon.png")"
    else
        ICO_FILE=""
    fi

    # Write the VBScript
    cat > "$VBS_FILE" <<VBSEOF
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "$LINK_FILE"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "$BAT_FILE"
oLink.WorkingDirectory = "$(cygpath -w "$CURRENT_DIR" 2>/dev/null || echo "$CURRENT_DIR")"
$([ -n "$ICO_FILE" ] && echo "oLink.IconLocation = \"$ICO_FILE\"")
oLink.Save
VBSEOF

    # Run VBScript and clean up
    cscript //nologo "$(cygpath -w "$VBS_FILE" 2>/dev/null || echo "$VBS_FILE")"
    rm -f "$VBS_FILE"
    echo "✅ Desktop shortcut created at: $LINK_FILE"

    "$PYTHON" main.py

elif [ "$PLATFORM" == "linux" ]; then
    gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings \
    "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/']"
    gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ name 'Launch Sabrina AI'
    gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ command "$CURRENT_DIR/shortcutkey.sh"
    gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ binding '<Super><Shift>S'
    ./shortcutkey.sh
fi