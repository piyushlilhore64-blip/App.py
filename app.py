from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
import os

app = Flask(__name__)

# Load users from JSON
def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "server running"}), 200

# API login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    users = load_users()

    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400

    if username in users and users[username] == password:
        return jsonify({"status": "success", "message": "Login successful"}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

# Admin panel
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    users = load_users()
    if request.method == "POST":
        action = request.form.get("action")
        username = request.form.get("username")
        password = request.form.get("password")

        if action == "add":
            users[username] = password
        elif action == "delete":
            users.pop(username, None)
        elif action == "update":
            if username in users:
                users[username] = password

        save_users(users)
        return redirect(url_for("admin_panel"))

    return render_template("admin.html", users=users)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
