#!/bin/bash

set -e

echo "🔧 Starting Sabrina AI setup..."

# -----------------------------
# Detect Platform
# -----------------------------
OS="$(uname -s 2>/dev/null || echo "Windows")"

case "$OS" in
    Linux*)   PLATFORM="linux" ;;
    Darwin*)  PLATFORM="mac" ;;
    MINGW*|MSYS*|CYGWIN*) PLATFORM="windows" ;;
    *)
        # Fallback: check if we're on Windows via environment
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
    echo "⚡ Installing llama-cpp-python with CUDA..."
    CMAKE_ARGS="-DGGML_CUDA=on" "$PIP" install llama-cpp-python
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
elif [ "$PLATFORM" == "mac" ]; then
    user_os="macOS $(sw_vers -productVersion)"
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
# Create User Metadata
# -----------------------------
METADATA_DIR="UserPreferences"
METADATA_FILE="${METADATA_DIR}/userMetaData.json"

mkdir -p "$METADATA_DIR"

cat > "$METADATA_FILE" <<EOF
{
    "version": "1.0",
    "user": {
        "name": "${user_name}",
        "gender": "${user_gender}",
        "user_os": "${user_os}",
        "default_shell": "${default_shell}"
    },
    "preferences": {}
}
EOF

echo "✅ User metadata saved to $METADATA_FILE"

# -----------------------------
# Final Message
# -----------------------------
echo ""
echo "🚀 Setup complete!"
echo ""
echo "👉 Activate your virtual environment before running:"

if [ "$PLATFORM" == "windows" ]; then
    echo "   .venv\\Scripts\\activate"
else
    echo "   source .venv/bin/activate"
fi

echo ""
echo "   Then run: python main.py"