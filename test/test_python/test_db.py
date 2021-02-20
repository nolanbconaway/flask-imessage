"""Test the DB module."""
import pytest
from flask_imessage import config, db

# mocking parse contacts tsv for this. id, name, phone
FAKE_TSV = """
fakeida\tHuman Readable Name\ta
fakeidb\tHuman Readable Name\tb
"""


@pytest.fixture
def contacts_tsv(monkeypatch, tmp_path):
    """Make a fake TSV file for testing."""
    tmpfile = tmp_path / "contacts.tsv"
    monkeypatch.setattr(config, "CACHED_CONTACTS_PATH", tmpfile)
    tmpfile.write_text(FAKE_TSV)
    yield tmpfile


def test_get_flat_messages(monkeypatch, contacts_tsv):
    flat_messages = [
        dict(chat_id="a", sender_id="a"),
        dict(chat_id="b,a", sender_id="a"),
        dict(chat_id="b,a", sender_id="b"),
        dict(chat_id="b", sender_id="b"),
    ]
    monkeypatch.setattr(db, "query", lambda x: flat_messages)
    result = db.get_flat_messages()

    assert len(result) == 4
    assert all([d["sender_name"] == "Human Readable Name" for d in result])


def test_group_flat_messages():
    """Test the core chat grabber."""
    flat_messages = [
        dict(chat_id="a", date_unix=1),
        dict(chat_id="b", date_unix=2),
        dict(chat_id="a", date_unix=3),
        dict(chat_id="b", date_unix=4),
    ]

    grouped = db.group_flat_messages(flat_messages)

    assert len(grouped) == 2
    assert list(map(len, grouped.values())) == [2, 2]
