"""Handlers for osascript + imessage."""
import subprocess

from . import config


class InvalidPhoneError(Exception):
    pass


def sanitize_phone(phone: str) -> str:
    """Sanitize a phone number for applescript.

    Best if nothing but numbers. can be 10 digits or 11 if we include a +1 or whatever.
    """
    phone_numbers = "".join(filter(str.isdigit, phone))
    if len(phone_numbers) not in (10, 11):
        raise InvalidPhoneError(f"Invalid phone: {phone}")

    return phone_numbers


def send_message(phone: str, message: str, account_id: str):
    applescript = config.WHEREAMI / "osascript/send_message.applescript"
    command = ["osascript", applescript, sanitize_phone(phone), message, account_id]
    return subprocess.run(command, capture_output=True, check=True)
