#!/usr/bin/env bash
set -euo pipefail

cd backend
[ -d ".venv" ] && source .venv/bin/activate
black --check app
flake8 app --max-line-length=120 --extend-ignore=E203,W503,E501
mypy app --ignore-missing-imports

cd ../frontend
npm run lint
npx tsc --noEmit
echo "All lint & type checks passed!"
