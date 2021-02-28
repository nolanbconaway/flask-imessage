"""Build the web application."""
import os

from flask import Flask, jsonify, render_template, request

from . import scheduler, socketio


def create_app() -> Flask:
    """Make the application."""
    app = Flask(__name__)

    @app.route("/")
    def home():
        """Render the main page."""
        return render_template("home.html")

    @app.route("/set-session", methods=["POST"])
    def set_session_cookie():
        data = {"key": request.form["key"], "value": request.form["value"]}
        response = jsonify(dict(_success=True, data=data))
        response.set_cookie(data["key"], data["value"])
        return response

    @app.route("/get-session", methods=["POST"])
    def get_session_cookie():
        value = request.cookies.get(request.form["key"])  # null if not defined
        return jsonify(
            dict(_success=True, data=dict(key=request.form["key"], value=value))
        )

    # register scheduler and socket extensions, routes
    app.register_blueprint(scheduler.bp)
    app.register_blueprint(socketio.bp)

    socketio.socketio.init_app(app)
    scheduler.scheduler.init_app(app)

    print("Serving socketio via:", socketio.socketio.server.eio.async_mode)

    # only start the scheduler when running the app. not needed for test.
    if os.getenv("ENV", "DEV") != "TEST":
        print("Running the scheduler")
        scheduler.scheduler.start()

    return app
