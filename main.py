import os
import json
import time
from flask import Flask, jsonify, request

app = Flask(__name__)

# 🔐 SECRET KEY (ENV ONLY)
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable not set")

# =========================
# GLOBAL ALERT STORAGE
# =========================
CURRENT_ALERT = {
    "id": 0,
    "title": "",
    "message": "",
    "active": False,
    "status": "pending"  # pending | approved | declined
}

# =========================
# HELPERS
# =========================
def read_json_file(filename, default):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return default

def write_json_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def read_lines(filename):
    try:
        with open(filename, "r") as f:
            return [l.strip() for l in f if l.strip()]
    except:
        return []

def require_secret(req):
    return req.headers.get("X-SECRET-KEY") == SECRET_KEY

# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return "Alert + Stats API Running"

# =========================
# ALERT APIs
# =========================
@app.route("/alert", methods=["GET"])
def get_alert():
    return jsonify(CURRENT_ALERT)

@app.route("/set-alert", methods=["POST"])
def set_alert():
    if not require_secret(request):
        return jsonify({"error": "unauthorized"}), 401

    data = request.json or {}

    CURRENT_ALERT["id"] += 1
    CURRENT_ALERT["title"] = data.get("title", "Payment Alert")
    CURRENT_ALERT["message"] = data.get("message", "")
    CURRENT_ALERT["active"] = data.get("active", True)
    CURRENT_ALERT["status"] = data.get("status", "pending")

    return jsonify({"status": "alert updated", "id": CURRENT_ALERT["id"]})

@app.route("/clear-alert", methods=["POST"])
def clear_alert():
    if not require_secret(request):
        return jsonify({"error": "unauthorized"}), 401

    CURRENT_ALERT["active"] = False
    return jsonify({"status": "alert cleared"})

# =========================
# PAYMENT LOGGING (BOT → API)
# =========================
@app.route("/log-payment", methods=["POST"])
def log_payment_api():
    if not require_secret(request):
        return jsonify({"error": "unauthorized"}), 401

    data = request.json or {}

    payments = read_json_file("payments.json", [])
    payments.append(data)
    write_json_file("payments.json", payments)

    return jsonify({"status": "payment logged"})

# =========================
# RESET PAYMENTS (ADMIN)
# =========================
@app.route("/reset-payments", methods=["POST"])
def reset_payments():
    if not require_secret(request):
        return jsonify({"error": "unauthorized"}), 401

    write_json_file("payments.json", [])
    return jsonify({"status": "payments reset"})

# =========================
# RESET EVERYTHING (ADMIN)
# =========================
@app.route("/reset-all", methods=["POST"])
def reset_all():
    if not require_secret(request):
        return jsonify({"error": "unauthorized"}), 401

    write_json_file("payments.json", [])
    CURRENT_ALERT["active"] = False

    return jsonify({"status": "all data reset"})

# =========================
# STATS API (DASHBOARD)
# =========================
@app.route("/stats", methods=["GET"])
def get_stats():
    payments = read_json_file("payments.json", [])

    today = time.strftime("%Y-%m-%d")

    total_collection = 0
    today_collection = 0

    sold_500 = 0
    sold_1000 = 0
    revenue_500 = 0
    revenue_1000 = 0

    for p in payments:
        if p.get("status") != "approved":
            continue

        amount = int(p.get("amount", 0))
        qty = int(p.get("quantity", 1))

        total_collection += amount

        if today in str(p.get("time", "")):
            today_collection += amount

        if p.get("coupon_type") == "500_off":
            sold_500 += qty
            revenue_500 += amount

        if p.get("coupon_type") == "500_off_1000":
            sold_1000 += qty
            revenue_1000 += amount

    stock_500_left = len(read_lines("500OFF.json"))
    stock_1000_left = len(read_lines("1000OFF500.json"))

    return jsonify({
        "total_collection": total_collection,
        "today_collection": today_collection,
        "500OFF": {
            "sold": sold_500,
            "left": stock_500_left,
            "collection": revenue_500
        },
        "1000OFF500": {
            "sold": sold_1000,
            "left": stock_1000_left,
            "collection": revenue_1000
        }
    })

# =========================
# START SERVER
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
