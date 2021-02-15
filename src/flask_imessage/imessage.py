"""Handlers for osascript + imessage."""
import subprocess

from . import config


class InvalidPhoneError(Exception):
    pass


def sanitize_phone(phone: str) -> str:
    """Sanitize a phone number for applescript.

    Best if nothing but numbers. Can be 10 - 14 digits depending on country code.
    """
    phone_numbers = "".join(filter(str.isdigit, phone))
    if len(phone_numbers) not in (10, 11, 12, 13, 14):
        raise InvalidPhoneError(f"Invalid phone: {phone}")

    return phone_numbers


def send_message(phone: str, message: str, account_id: str):
    """Send an iMessage to a phone number using an account."""
    applescript = config.WHEREAMI / "osascript/send_message.applescript"
    return subprocess.run(
        ["osascript", applescript, sanitize_phone(phone), message, account_id],
        capture_output=True,
        check=True,
    )
