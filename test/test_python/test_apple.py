"""Test the apple module."""
import pytest
from flask_imessage import apple, config

FAKE_TSV = """
id1\tfake name1\t111-111-1111
id2\tfake name2\t111-111-1112
id3\tfake name3\t111-111-1113
"""


@pytest.fixture
def contacts_tsv(monkeypatch, tmp_path):
    """Make a fake TSV file for testing."""
    tmpfile = tmp_path / "contacts.tsv"
    monkeypatch.setattr(config, "CACHED_CONTACTS_PATH", tmpfile)
    tmpfile.write_text(FAKE_TSV)
    yield tmpfile


@pytest.mark.parametrize(
    "phone, raises_error",
    [
        ("111-111-1111", False),
        ("+1-111-111-1111", False),
        ("11-111-1111", True),
        ("+12345-111-111-1111", True),
    ],
)
def test_sanitize_phone_error(phone: str, raises_error: bool):
    """Test that the phone number checks work."""
    if raises_error:
        with pytest.raises(apple.InvalidPhoneError):
            apple.sanitize_phone(phone, raise_error=True)
    else:
        apple.sanitize_phone(phone, raise_error=True)


def test_parse_contacts_tsv(contacts_tsv):
    data = apple.parse_contacts_tsv()
    assert len(data) == 3
    assert all(["contact_id" in d for d in data])
    assert all(["name" in d for d in data])
    assert all(["phone" in d for d in data])
