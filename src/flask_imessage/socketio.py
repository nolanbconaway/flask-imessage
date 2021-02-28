"""SocketIO events to be binded to the app."""
import datetime
import time
from subprocess import CalledProcessError

from flask import Blueprint
from flask_socketio import SocketIO

from . import apple, db

SECONDS_IN_A_DAY = 86400

bp = Blueprint("socket", __name__)
socketio = SocketIO()  # async_mode="gevent"


def update_messages(since: float = None, broadcast: bool = False):
    """Send messages to the client using the update_messages event.

    User has option to filter for messages after a unix timestamp, and also to
    broadcast to all clients.
    """
    where = f"""date_unix >= {since}""" if since is not None else ""
    messages = db.get_flat_messages(where)

    if not messages:
        return

    # log
    if broadcast:
        print(time.time(), f"Broadcasting {len(messages)} messages.")
    else:
        print(time.time(), f"Emitting {len(messages)} messages to client.")

    # emit
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

        - phone: a phone-number. group messages not supported rn.
        - account: an account guid
        - message: the text to send. attachments not supported rn.

    Responds via the `imessage_success` socket event if success, or `application_error`
    if failed.
    """
    try:
        apple.send_message(data["phone"], data["message"], data["account"])
        time.sleep(5)
        socketio.emit("imessage_success", datetime.datetime.utcnow().timestamp())

    # if an expected error, send the user some info and exit
    except apple.InvalidPhoneError as e:
        socketio.emit("application_error", str(e))

    except CalledProcessError as e:
        socketio.emit("application_error", e.stderr.decode())
