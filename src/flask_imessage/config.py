"""App configuration."""
from pathlib import Path

DB_PATH = Path.home() / "Library/Messages/chat.db"
WHEREAMI = Path(__file__).parent.absolute()

# this is a TSV file that takes a minute to generate
# so regenerate it every now and again async.
CACHED_CONTACTS_PATH = WHEREAMI / ".cache/contacts.tsv"
