import os, json
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, messaging

app = Flask(__name__)

# Firebase init (HTTP v1)
cred = credentials.Certificate(
    json.loads(os.environ["FIREBASE_CREDENTIALS"])
)
firebase_admin.initialize_app(cred)

@app.route("/")
def home():
    return "Payment Push API Running"

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
