"""Test the production server runs."""
import subprocess
import time

import requests


def test_production_server():
    """Confirm that the app is being served."""
    command = ["python", "-m", "flask_imessage.serve", "--port=5000"]
    with subprocess.Popen(command) as proc:
        time.sleep(0.5)
        resp = requests.get("http://localhost:5000")
        resp.raise_for_status()
        proc.kill()
