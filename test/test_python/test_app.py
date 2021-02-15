"""Test the socketio bindings in the app module."""
import time

import pytest
from flask_imessage import app, db, socket

# mocking get flat to return this
FAKE_FLAT_MESSAGES = [
    dict(chat_id="a", sender_id="foo", is_from_me=0),
    dict(chat_id="a", sender_id="bar", is_from_me=0),
    dict(chat_id="b", sender_id="foo", is_from_me=0),
    dict(chat_id="b", sender_id="bar", is_from_me=1),
]

# add programatic columns to flat messages
for i, message in enumerate(FAKE_FLAT_MESSAGES):
    message["message_id"] = str(i)
    message["date_unix"] = time.time() - i
    message["message_text"] = f"message number {i}"


@pytest.fixture
def app_and_socket_client(monkeypatch):
    """Application fixture."""
    monkeypatch.setattr(db, "query", lambda x: FAKE_FLAT_MESSAGES)
    monkeypatch.setenv("ENV", "TEST")
    application = app.create_app()
    with application.test_client() as client:
        sio = socket.socketio.test_client(application, flask_test_client=client)
        yield client, sio


def test_socketio_connect(app_and_socket_client):
    """Test that the user gets messages on connect."""
    client, socketio = app_and_socket_client

    # user ought to have recieved some messages
    connect_response = socketio.get_received()
    assert len(connect_response) == 1

    connect_response = connect_response[0]
    assert connect_response["name"] == "update_messages"
