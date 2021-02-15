"""Test the DB module."""
import pytest
from flask_imessage import db


def test_get_account_id(monkeypatch):
    monkeypatch.setattr(db, "query", lambda x: [dict(account_id=1)])
    assert db.get_account_for_chat("FAKE") == 1

    monkeypatch.setattr(db, "query", lambda x: [])
    with pytest.raises(db.InvalidServiceError):
        db.get_account_for_chat("FAKE")
