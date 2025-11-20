#!/bin/bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Initialize and sync submodule
git submodule update --init --recursive
