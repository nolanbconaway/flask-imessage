"""Test the socketio bindings in the app module."""
import subprocess
import time

import pytest
from flask_imessage import app, apple, config, db, socketio

# mocking get flat to return this
FAKE_FLAT_MESSAGES = [
    dict(is_from_me=0, chat_id="a,b", sender_id="a"),
    dict(is_from_me=0, chat_id="b,a", sender_id="b"),
    dict(is_from_me=0, chat_id="b", sender_id="b"),
    dict(is_from_me=0, chat_id="b", sender_id="b"),
]


@pytest.fixture
def app_clients(monkeypatch, tmp_path):
    """Provide a dict of test clients."""
    monkeypatch.setattr(db, "query", lambda x: FAKE_FLAT_MESSAGES)
    monkeypatch.setenv("ENV", "TEST")

    # patch contacts tsv
    tmpfile = tmp_path / "contacts.tsv"
    monkeypatch.setattr(config, "CACHED_CONTACTS_PATH", tmpfile)
    tmpfile.write_text("")  ## empty data

    application = app.create_app()
    with application.test_client() as client:
        sio = socketio.socketio.test_client(application, flask_test_client=client)
        yield dict(app=client, socketio=sio, contacts_tsv=tmpfile)


def test_socketio_connect(app_clients):
    """Test that the user gets messages on connect."""
    socketio = app_clients["socketio"]

    # user ought to have recieved some messages
    connect_response = socketio.get_received()
    assert len(connect_response) == 1

    connect_response = connect_response[0]
    assert connect_response["name"] == "update_messages"


def test_socketio_request_messages(app_clients):
    """Test that the user gets relevent data when messages are requested."""
    socketio = app_clients["socketio"]
    socketio.get_received()  # clear the connect response

    socketio.emit("request_messages", {"since": 0})
    recieved = socketio.get_received()
    assert len(recieved) == 1
    assert recieved[0]["name"] == "update_messages"


def test_socketio_send_messages(app_clients, monkeypatch):
    """Test that the user gets relevent data when messages are sent."""
    monkeypatch.setattr(apple, "send_message", lambda *x: None)
    monkeypatch.setattr(time, "sleep", lambda *x: None)

    socketio = app_clients["socketio"]
    socketio.get_received()  # clear the connect response

    socketio.emit(
        "send_message", {"phone": "FAKE", "message": "FAKE", "account": "FAKE"}
    )
    recieved = socketio.get_received()
    assert len(recieved) == 1
    assert recieved[0]["name"] == "imessage_success"


def test_socketio_send_messages_error(app_clients, monkeypatch):
    """Test that the user gets relevent data when messages are sent."""
    socketio = app_clients["socketio"]
    socketio.get_received()  # clear the connect response

    monkeypatch.setattr(time, "sleep", lambda *x: None)

    def fake_send(*x):
        raise apple.InvalidPhoneError

    monkeypatch.setattr(apple, "send_message", fake_send)

    socketio.emit(
        "send_message", {"phone": "FAKE", "message": "FAKE", "account": "FAKE"}
    )
    recieved = socketio.get_received()
    assert len(recieved) == 1
    assert recieved[0]["name"] == "application_error"


def test_cookie_setter_and_getter(app_clients):
    client = app_clients["app"]

    # set the cookie, client returns data as-is
    data = client.post("/set-session", data=dict(key="something", value="123")).json
    assert data["_success"]
    assert data["data"]["key"] == "something"
    assert data["data"]["value"] == "123"

    # get the cookie; response should be the same
    data = client.post("/get-session", data=dict(key="something")).json
    assert data["_success"]
    assert data["data"]["key"] == "something"
    assert data["data"]["value"] == "123"
