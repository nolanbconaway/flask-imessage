"""Test the DB module."""
import pytest
from flask_imessage import db


def test_get_account_for_chat(monkeypatch):
    """Test the utility to query the last account per chat."""
    monkeypatch.setattr(db, "query", lambda x: [dict(account_id=1)])
    assert db.get_account_for_chat("FAKE") == 1

    monkeypatch.setattr(db, "query", lambda x: [])
    with pytest.raises(db.InvalidServiceError):
        db.get_account_for_chat("FAKE")


def test_group_flat_messages(monkeypatch):
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
