#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_ACTIVATE="$ROOT_DIR/.venv/bin/activate"

if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "Virtual environment not found at $VENV_ACTIVATE"
    echo "Create it first with: python3 -m venv .venv"
    exit 1
fi

# shellcheck disable=SC1091
source "$VENV_ACTIVATE"

cd "$ROOT_DIR"
python -m pytest --cov=src --cov-report=term-missing "$@"
