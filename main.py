import os
from flask import Flask, request, jsonify

app = Flask(__name__)

latest_alert = {"id": 0, "message": ""}

SECRET = os.environ.get("SECRET_KEY")  # <-- FROM RENDER

@app.route("/")
def home():
    return "Payment Alert API Running"

@app.route("/send", methods=["POST"])
def send_alert():
    data = request.json

    if data.get("secret") != SECRET:
        return jsonify({"status": "unauthorized"}), 403

    latest_alert["id"] += 1
    latest_alert["message"] = data.get("message")
    return jsonify({"status": "ok"})

@app.route("/get", methods=["GET"])
def get_alert():
    return jsonify(latest_alert)

app.run(host="0.0.0.0", port=8080)
