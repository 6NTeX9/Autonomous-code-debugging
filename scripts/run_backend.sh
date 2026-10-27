#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
PORT="${PORT:-8001}"

echo "🚀 Starting Autonomous Code Debugging Agent Backend on http://localhost:$PORT..."
cd "$ROOT_DIR/backend"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

export PYTHONPATH="$ROOT_DIR/backend"
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload
