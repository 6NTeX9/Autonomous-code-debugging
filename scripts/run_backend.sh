#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting Autonomous Code Debugging Agent Backend..."
cd "$ROOT_DIR/backend"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

export PYTHONPATH="$ROOT_DIR/backend"
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
