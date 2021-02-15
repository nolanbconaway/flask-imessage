"""Build the web application."""
import datetime
import time
from subprocess import CalledProcessError

from flask import Flask, render_template
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO

from . import db, imessage

app = Flask(__name__)
socketio = SocketIO(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


@app.route("/")
def home():
    """Render the main page."""
    return render_template("home.html")


@socketio.event
def request_messages(data):
    """Send requested messages since to the client.

    Assumes the data contains a `since` key, after which all messages are returned.
    `since` is a unix timestamp.

    Responds via the `update_messages` socket event.
    """
    messages = db.get_flat_messages(f"""date_unix >= {data["since"]}""")
    if messages:
        print(f"Emitting {len(messages)} messages to client.")
        socketio.emit("update_messages", db.group_flat_messages(messages))


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
    "interval", id="broadcast_update", seconds=2, misfire_grace_time=10, max_instances=1
)
def broadcast_update():
    """Broadcast message updates to clients on an interval.

    Runs every 2 seconds, checking for messages in the last 10 seconds to be safe.
    It will only emit a socket event if there is new data.
    """
    unix_stamp = time.time() - 10  # use time.time bc datetime.timestamp is WEIRD.
    messages = db.get_flat_messages(f"""date_unix >= {unix_stamp}""")
    if messages:
        print(f"Broadcasting {len(messages)} messages.")
        socketio.emit(
            "update_messages", db.group_flat_messages(messages), broadcast=True
        )
