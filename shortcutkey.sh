#!/bin/bash

# Get the directory where this script lives (works regardless of where it's called from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

PYTHON="$SCRIPT_DIR/.venv/bin/python"

if [ ! -f "$PYTHON" ]; then
    echo "❌ Python not found at $PYTHON"
    echo "   Please run setup.sh first."
    exit 1
fi

"$PYTHON" main.py