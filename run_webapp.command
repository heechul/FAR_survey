#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -x ".venv/bin/python" ]; then
  echo "Virtual environment not found at .venv/bin/python"
  echo "Setup steps:"
  echo "  python3 -m venv .venv"
  echo "  .venv/bin/pip install -r requirements.txt"
  read -n 1 -s -r -p "Press any key to close..."
  echo
  exit 1
fi

echo "Starting FAR Survey web app..."
echo "Open http://127.0.0.1:5000 in your browser"

".venv/bin/python" webapp.py
