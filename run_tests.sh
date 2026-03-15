#!/usr/bin/env bash
# Simple developer test runner: creates a venv if missing, installs dev deps, runs pytest
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
REQ="$ROOT_DIR/requirements-dev.txt"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found in PATH"
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtualenv in $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

if [ ! -f "$REQ" ]; then
  echo "requirements-dev.txt not found at $REQ"
  exit 1
fi

pip install --upgrade pip setuptools wheel
pip install -r "$REQ"

# Run pytest with project root on PYTHONPATH so tests can import `src`
export PYTHONPATH="$ROOT_DIR"
pytest -q
