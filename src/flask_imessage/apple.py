"""Handlers for osascript + imessage."""
import csv
import subprocess
import typing

from . import config


class InvalidPhoneError(Exception):
    """Raised when an account ID cannot be located for a chat."""

    pass


def sanitize_phone(phone: str, raise_error: bool = False) -> str:
    """Sanitize a phone number for applescript.

    Best if nothing but numbers. Can be 10 - 14 digits depending on country code.
    """
    phone_numbers = "".join(filter(str.isdigit, phone))
    if len(phone_numbers) not in (10, 11, 12, 13, 14):
        if raise_error:
            raise InvalidPhoneError(f"Invalid phone: {phone}")
        else:
            return phone
    return phone_numbers[-10:]  # IDC about country code


def send_message(phone: str, message: str, account_id: str):
    """Send an iMessage to a phone number using an account."""
    applescript = config.WHEREAMI / "osascript/send_message.applescript"
    return subprocess.run(
        ["osascript", applescript, sanitize_phone(phone), message, account_id],
        capture_output=True,
        check=True,
    )


def parse_contacts_tsv() -> typing.List[typing.Dict[str, str]]:
    """Parse the cached contacts TSV file and return a list of dicts."""
    if not config.CACHED_CONTACTS_PATH.exists():
        return []

    with config.CACHED_CONTACTS_PATH.open("r") as tsvfile:
        reader = csv.DictReader(
            tsvfile, delimiter="\t", fieldnames=("contact_id", "name", "phone")
        )
        contacts = sorted(list(reader), key=lambda x: x["contact_id"])

    for d in contacts:
        d["phone"] = sanitize_phone(d["phone"])

    return contacts


def get_contacts():
    """Run the contacts applescript and parse the csv.

    Expected structure is: id<TAB>name<TAB>phone

    Result will have a single record per phone number in the database, so possible
    duplicate IDs. This job is pretty slow.
    """
    applescript = config.WHEREAMI / "osascript/get_contacts.applescript"
    return subprocess.run(
        ["osascript", applescript], capture_output=True, check=True
    ).stdout.decode()
