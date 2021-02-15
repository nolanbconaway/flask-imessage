"""SocketIO events to be binded to the app."""
import datetime
import time
from subprocess import CalledProcessError

from flask import Blueprint
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO

from . import db, imessage

SECONDS_IN_A_DAY = 86400

bp = Blueprint("socket", __name__)
socketio = SocketIO()
scheduler = APScheduler()


def update_messages(since: float = None, broadcast: bool = False):
    """Send messages to the client using the update_messages event.

    User has option to filter for messages after a unix timestamp, and also to
    broadcast to all clients.
    """
    where = f"""date_unix >= {since}""" if since is not None else ""
    messages = db.get_flat_messages(where)
    if messages:
        if broadcast:
            print(f"Broadcasting {len(messages)} messages.")
        else:
            print(f"Emitting {len(messages)} messages to client.")
        socketio.emit(
            "update_messages", db.group_flat_messages(messages), broadcast=broadcast
        )


@socketio.on("connect")
def on_connect():
    """Send user a bulk update of messages on connect."""
    # use time.time bc datetime.timestamp is WEIRD.
    unix_stamp = time.time() - (SECONDS_IN_A_DAY * 365)
    update_messages(since=unix_stamp)


@socketio.event
def request_messages(data):
    """Send requested messages since to the client.

    Assumes the data contains a `since` key, after which all messages are returned.
    `since` is a unix timestamp.

    Responds via the `update_messages` socket event.
    """
    update_messages(since=data["since"])


@socketio.event
def send_message(data):
    """Send a message.

    Expected data to contain keys:

        - chatId: a phone-number like chat ID. group messages not supported rn.
        - message: the text to send. attachments not supported rn.

    Responds via the `imessage_success` socket event if success, or `imessage_error`
    if failed.
    """
    try:
        account_id = db.get_account_for_chat(data["chatId"])
        imessage.send_message(data["chatId"], data["message"], account_id)
        time.sleep(5)
        socketio.emit("imessage_success", datetime.datetime.utcnow().timestamp())

    # if an expected error, send the user some info and exit
    except (imessage.InvalidPhoneError, db.InvalidServiceError) as e:
        socketio.emit("imessage_error", str(e))

    except CalledProcessError as e:
        socketio.emit("imessage_error", e.stderr.decode())


@scheduler.task(
    "interval", id="broadcast", seconds=2, max_instances=1, misfire_grace_time=5
)
def broadcast_update():
    """Broadcast message updates to clients on an interval.

    Runs every 2 seconds, checking for messages in the last 10 seconds to be safe.
    It will only emit a socket event if there is new data.
    """
    update_messages(since=time.time() - 10, broadcast=True)
