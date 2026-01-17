import os
from flask import Flask, jsonify, request

app = Flask(__name__)

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

# Global alert storage
CURRENT_ALERT = {
    "id": 0,
    "title": "",
    "message": "",
    "active": False,
    "status": "pending"  # pending | approved | rejected
}

@app.route("/")
def home():
    return "Alert API Running"

# GET alert (MIT App Inventor will call this)
@app.route("/alert", methods=["GET"])
def get_alert():
    return jsonify(CURRENT_ALERT)

# SET alert (server / admin will call this)
@app.route("/set-alert", methods=["POST"])
def set_alert():
    key = request.headers.get("X-SECRET-KEY")
    if key != SECRET_KEY:
        return jsonify({"error": "unauthorized"}), 401

    data = request.json or {}

    CURRENT_ALERT["id"] += 1
    CURRENT_ALERT["title"] = data.get(
        "title", "Payment Approval Request"
    )
    CURRENT_ALERT["message"] = data.get("message", "")
    CURRENT_ALERT["active"] = data.get("active", True)
    CURRENT_ALERT["status"] = data.get("status", "pending")

    return jsonify({
        "status": "alert updated",
        "id": CURRENT_ALERT["id"]
    })

# OPTIONAL: clear alert after showing once
@app.route("/clear-alert", methods=["POST"])
def clear_alert():
    CURRENT_ALERT["active"] = False
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
