#!/usr/bin/env bash
set -euo pipefail

cd backend
[ -d ".venv" ] && source .venv/bin/activate
pytest -v tests/

cd ../frontend
npm run build
echo "All tests passed!"
