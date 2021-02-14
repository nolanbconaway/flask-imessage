"""App configuration."""
from pathlib import Path

DB_PATH = Path.home() / "Library/Messages/chat.db"
WHEREAMI = Path(__file__).parent.absolute()
