import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SKILLS_DIR = BASE_DIR / "skills"
PROFILES_DIR = BASE_DIR / "browser_profiles"

DATA_DIR.mkdir(parents=True, exist_ok=True)
SKILLS_DIR.mkdir(parents=True, exist_ok=True)
PROFILES_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "app.db"
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "supersecretdefaultkeythirtytwoch")
API_BEARER_SECRET = os.getenv("API_BEARER_SECRET", "local-dev-bearer-token")
HEADLESS = os.getenv("HEADLESS", "true").lower() in ("true", "1", "yes")
