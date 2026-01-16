import os
from flask import Flask, jsonify, request

app = Flask(__name__)

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

# global alert storage
CURRENT_ALERT = {
    "id": 0,
    "title": "",
    "message": "",
    "active": False
}

@app.route("/")
def home():
    return "Alert API Running"

@app.route("/alert")
def get_alert():
    return jsonify(CURRENT_ALERT)

@app.route("/set-alert", methods=["POST"])
def set_alert():
    key = request.headers.get("X-SECRET-KEY")
    if key != SECRET_KEY:
        return jsonify({"error": "unauthorized"}), 401

    data = request.json or {}

    # increment ID for every new alert
    CURRENT_ALERT["id"] += 1
    CURRENT_ALERT["title"] = data.get("title", "Alert")
    CURRENT_ALERT["message"] = data.get("message", "")
    CURRENT_ALERT["active"] = data.get("active", True)

    return jsonify({"status": "alert updated", "id": CURRENT_ALERT["id"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
