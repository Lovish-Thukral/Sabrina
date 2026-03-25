#!/bin/bash

set -e

MODEL_NAME="vosk-model-en-in-0.5"
MODEL_URL="https://alphacephei.com/vosk/models/${MODEL_NAME}.zip"
BASE_DIR="models/vosk"
MODEL_DIR="${BASE_DIR}/${MODEL_NAME}"
ZIP_FILE="model.zip"

echo "🔧 Starting Sabrina AI setup..."

# -----------------------------
# Install Python dependencies
# -----------------------------
echo "📦 Installing Python requirements..."
pip install -r requirements.txt

echo "📦 Installing PyTorch (CPU)..."
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# -----------------------------
# GPU Selection
# -----------------------------
echo ""
read -p "💻 Do you have an NVIDIA GPU? (y/n): " gpu_choice
gpu_choice=${gpu_choice:-n}

if [[ "$gpu_choice" =~ ^[Yy]$ ]]; then
    echo "⚡ Installing llama-cpp-python with CUDA..."
    CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python
else
    echo "🐢 Installing llama-cpp-python (CPU)..."
    pip install llama-cpp-python
fi

# -----------------------------
# Install Neutts
# -----------------------------
echo "🔊 Installing Neutts..."
pip install "neutts[llama]"
pip install "neutts[onnx]"

# -----------------------------
# Download Vosk Model
# -----------------------------
echo "🎤 Checking Vosk model..."

mkdir -p "$BASE_DIR"

if [ -d "$MODEL_DIR" ]; then
    echo "✅ Model already exists at $MODEL_DIR"
else
    echo "⬇️ Downloading Vosk Indian model (~1GB)..."

    wget -O "$ZIP_FILE" "$MODEL_URL"

    echo "📦 Extracting..."
    unzip "$ZIP_FILE" -d "$BASE_DIR"

    rm "$ZIP_FILE"

    echo "✅ Model installed at $MODEL_DIR"
fi

# -----------------------------
# Final Message
# -----------------------------
echo ""
echo "🚀 Setup complete!"
echo "👉 Run your app using:"
echo "python main.py"