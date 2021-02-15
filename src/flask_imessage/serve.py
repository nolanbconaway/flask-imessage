"""Run a production (???) server."""

"""Run the wsgi server."""
import argparse
import os

from .app import create_app
from .socketio import socketio

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "5000")))
    args = parser.parse_args()

    socketio.run(create_app(), port=args.port, host="0.0.0.0")
