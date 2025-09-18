from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this for production

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

connections = []

# ---------------- Admin Panel ----------------
@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users = load_users()
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
    username = request.form.get("username")
    password = request.form.get("password")
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
    username = request.form.get("username")
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
    return redirect(url_for("admin_panel"))

# ---------------- HTTP Injector Login ----------------
@app.route("/login_user", methods=["POST"])
def login_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
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
