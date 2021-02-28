"""Test the socketio bindings in the app module."""
import pytest
from flask_imessage import app, config, db, socketio


@pytest.fixture
def contacts_tsv(monkeypatch, tmp_path):
    """Make a fake TSV file for testing."""
    tmpfile = tmp_path / "contacts.tsv"
    monkeypatch.setattr(config, "CACHED_CONTACTS_PATH", tmpfile)
    tmpfile.write_text("")
    yield tmpfile


# mocking get flat to return this
FAKE_FLAT_MESSAGES = [
    dict(is_from_me=0, chat_id="a,b", sender_id="a"),
    dict(is_from_me=0, chat_id="b,a", sender_id="b"),
    dict(is_from_me=0, chat_id="b", sender_id="b"),
    dict(is_from_me=0, chat_id="b", sender_id="b"),
]


@pytest.fixture
def app_and_socket_client(monkeypatch):
    """Application fixture."""
    monkeypatch.setattr(db, "query", lambda x: FAKE_FLAT_MESSAGES)
    monkeypatch.setenv("ENV", "TEST")
    application = app.create_app()
    with application.test_client() as client:
        sio = socketio.socketio.test_client(application, flask_test_client=client)
        yield client, sio


def test_socketio_connect(app_and_socket_client):
    """Test that the user gets messages on connect."""
    _, socketio = app_and_socket_client

    # user ought to have recieved some messages
    connect_response = socketio.get_received()
    assert len(connect_response) == 1

    connect_response = connect_response[0]
    assert connect_response["name"] == "update_messages"


def test_cookie_setter_and_getter(app_and_socket_client):
    client, _ = app_and_socket_client

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
