from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Fake DB
keys = {
    "demo123": {"expiry": time.time() + 3600},  # 1 hour
}
maintenance_mode = False

ADMIN_USER = "admin"
ADMIN_PASS = "123456"

@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.json
    if data.get("username") == ADMIN_USER and data.get("password") == ADMIN_PASS:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid login"}), 401

@app.route("/add_key", methods=["POST"])
def add_key():
    data = request.json
    key = data["key"]
    duration = int(data["duration"])  # in seconds
    keys[key] = {"expiry": time.time() + duration}
    return jsonify({"status": "success", "key": key, "expiry": keys[key]["expiry"]})

@app.route("/delete_key", methods=["POST"])
def delete_key():
    data = request.json
    key = data["key"]
    if key in keys:
        del keys[key]
        return jsonify({"status": "success", "key": key})
    return jsonify({"status": "error", "message": "Key not found"}), 404

@app.route("/list_keys", methods=["GET"])
def list_keys():
    now = time.time()
    response = {}
    for k, v in keys.items():
        response[k] = {
            "expiry": v["expiry"],
            "expired": now > v["expiry"]
        }
    return jsonify(response)

@app.route("/check_key", methods=["POST"])
def check_key():
    global maintenance_mode
    if maintenance_mode:
        return jsonify({"status": "error", "message": "Maintenance mode active"}), 503

    data = request.json
    key = data["key"]
    user = keys.get(key)
    if not user:
        return jsonify({"status": "error", "message": "Invalid key"}), 401
    if time.time() > user["expiry"]:
        return jsonify({"status": "error", "message": "Key expired"}), 403
    return jsonify({"status": "success", "message": "Access granted"})

@app.route("/maintenance", methods=["POST"])
def toggle_maintenance():
    global maintenance_mode
    data = request.json
    maintenance_mode = data.get("status", False)
    return jsonify({"status": "success", "maintenance": maintenance_mode})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
