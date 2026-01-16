import os, json
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, messaging

app = Flask(__name__)

# -------------------------
# OLD SYSTEM (polling)
# -------------------------
latest_alert = {"id": 0, "message": ""}
SECRET = os.environ.get("SECRET_KEY")

# -------------------------
# FIREBASE INIT
# -------------------------
cred = credentials.Certificate(
    json.loads(os.environ["FIREBASE_CREDENTIALS"])
)
firebase_admin.initialize_app(cred)

@app.route("/")
def home():
    return "Payment Alert API Running"

# -------------------------
# OLD SEND (for polling / channel use)
# -------------------------
@app.route("/send", methods=["POST"])
def send_alert():
    data = request.json

    if data.get("secret") != SECRET:
        return jsonify({"status": "unauthorized"}), 403

    msg = data.get("message", "")

    # update polling alert
    latest_alert["id"] += 1
    latest_alert["message"] = msg

    return jsonify({"status": "ok"})

@app.route("/get", methods=["GET"])
def get_alert():
    return jsonify(latest_alert)

# -------------------------
# NEW FIREBASE PUSH
# -------------------------
@app.route("/push", methods=["POST"])
def push():
    data = request.json
    token = data.get("token")
    message_text = data.get("message")

    if not token or not message_text:
        return jsonify({"error": "token or message missing"}), 400

    msg = messaging.Message(
        notification=messaging.Notification(
            title="Payment Alert ⚡",
            body=message_text
        ),
        token=token
    )

    messaging.send(msg)
    return jsonify({"status": "push sent"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
