"""Test the iMessage module."""
import pytest
from flask_imessage import imessage


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
        with pytest.raises(imessage.InvalidPhoneError):
            imessage.sanitize_phone(phone)
    else:
        imessage.sanitize_phone(phone)
