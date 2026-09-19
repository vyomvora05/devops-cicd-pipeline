import os
from datetime import datetime, timezone

from flask import Flask, jsonify

app = Flask(__name__)

BUILD_NUMBER = os.environ.get("BUILD_NUMBER", "local-dev")
GIT_COMMIT = os.environ.get("GIT_COMMIT", "unknown")[:7]
DEPLOYED_AT = datetime.now(timezone.utc).isoformat()


def add(a, b):
    # simple addition helper
    return a + b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


@app.route("/")
def home():
    return jsonify({
        "status": "healthy",
        "build_number": BUILD_NUMBER,
        "commit": GIT_COMMIT,
        "deployed_at": DEPLOYED_AT,
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port)
