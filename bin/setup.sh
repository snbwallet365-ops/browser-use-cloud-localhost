#!/usr/bin/env bash
set -euo pipefail

echo "==> Setting up Browser Use Cloud..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

cd backend
uv venv .venv --python 3.11 || uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
playwright install --with-deps chromium

cd ../frontend
npm install

cd ..
mkdir -p backend/data backend/skills backend/browser_profiles
[ ! -f .env ] && cp .env.example .env
echo "Setup complete!"
