from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "shop.db"

CHAT_MODEL = "claude-sonnet-4-6"
MAX_STEPS = 6
MAX_ROWS = 50
