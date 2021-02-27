"""Jobs to run async via scheduler."""
import time

from flask import Blueprint
from flask_apscheduler import APScheduler

from . import apple, config, socketio

bp = Blueprint("scheduler", __name__)
scheduler = APScheduler()


@scheduler.task(
    "interval", id="broadcast", seconds=2, max_instances=1, misfire_grace_time=10
)
def broadcast_update():
    """Broadcast message updates to clients on an interval.

    Runs every 2 seconds, checking for messages in the last 10 seconds to be safe.
    It will only emit a socket event if there is new data.
    """
    socketio.update_messages(since=time.time() - 10, broadcast=True)


@scheduler.task(
    "interval", id="contacts", seconds=600, max_instances=1, misfire_grace_time=120
)
def cache_contacts():
    """Run the applescript to cache contacts data.

    Runs every 10 minutes, and takes maybe 15-60 seconds, depending on number of
    contacts. Manually run via:

    osascript src/flask_imessage/osascript/get_contacts.applescript > src/flask_imessage/.cache/contacts.tsv
    """
    print(time.time(), "Updating contacts data")

    tsv = apple.get_contacts()

    if not config.CACHED_CONTACTS_PATH.parent.exists():
        config.CACHED_CONTACTS_PATH.parent.mkdir()
    config.CACHED_CONTACTS_PATH.write_text(tsv)

    print(time.time(), "Contacts data has been updated.")


@scheduler.task(
    "interval", id="sync", seconds=300, max_instances=1, misfire_grace_time=120
)
def cache_contacts():
    """Run the applescript to sync iMessages, in case Apple is not doing it.

    Runs every 5 minutes, and takes maybe 5 seconds.
    """
    print(time.time(), "Manually syncing iMessages")

    apple.sync_imessage()
    print(time.time(), "Sync Complete.")
