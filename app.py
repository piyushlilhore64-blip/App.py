from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production

USERS_FILE = "users.json"

# ---------------- User Management ----------------
def load_users():
    if not os.path.exists(USERS_FILE):
        # Auto-create with default admin if missing
        default_users = {"admin": "adm8n"}
        save_users(default_users)
        print("Created default users.json with admin:adm8n")
        return default_users

    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Reset if file is broken
            default_users = {"admin": "adm8n"}
            save_users(default_users)
            print("Fixed broken users.json, reset to admin:adm8n")
            return default_users

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

connections = []

# ---------------- Admin Panel ----------------
@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        users = load_users()

        # Debug info in logs
        print("DEBUG USERS:", users)
        print("LOGIN ATTEMPT:", username, password)

        if username in users and users[username] == password and username.lower() == "admin":
            session["admin"] = True
            return redirect(url_for("admin_panel"))
        else:
            return "Invalid credentials or not admin", 401
    return render_template("login.html")

@app.route("/")
def admin_panel():
    if not session.get("admin"):
        return redirect(url_for("login_page"))
    users = load_users()
    return render_template("index.html", users=users.keys(), connections=connections[-50:])

@app.route("/add_user", methods=["POST"])
def add_user():
    if not session.get("admin"):
        return redirect(url_for("login_page"))
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    users = load_users()
    if username in users:
        return "User already exists", 400
    users[username] = password
    save_users(users)
    return redirect(url_for("admin_panel"))

@app.route("/remove_user", methods=["POST"])
def remove_user():
    if not session.get("admin"):
        return redirect(url_for("login_page"))
    username = request.form.get("username", "").strip()
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
    return redirect(url_for("admin_panel"))

# ---------------- HTTP Injector Login ----------------
@app.route("/login_user", methods=["POST"])
def login_user():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    client_ip = request.remote_addr
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    users = load_users()
    if username in users and users[username] == password:
        msg = f"{timestamp} - {username} connected from {client_ip}"
        connections.append(msg)
        print(msg)
        return jsonify({"status": "success", "message": "Login successful"}), 200
    else:
        return jsonify({"status": "fail", "message": "Invalid credentials"}), 401

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
