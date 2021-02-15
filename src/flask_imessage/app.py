"""Build the web application."""
import os

from flask import Flask, render_template

from . import socketio


def create_app() -> Flask:
    """Make the application."""
    app = Flask(__name__)

    @app.route("/")
    def home():
        """Render the main page."""
        return render_template("home.html")

    # register scheduler and socket extensions, routes

    app.register_blueprint(socketio.bp)
    socketio.socketio.init_app(app)
    socketio.scheduler.init_app(app)

    # only start the scheduler when running the app. not needed for test.
    if os.getenv("ENV", "DEV") != "TEST":
        print("Running the scheduler")
        socketio.scheduler.start()

    return app
