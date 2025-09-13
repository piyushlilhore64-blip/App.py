from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")  # from Render env vars

USER_FILE = "users.json"

# Load users
def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r") as f:
        return json.load(f)

# Save users
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()
        user = next((u for u in users if u["username"] == username), None)
        if user and check_password_hash(user["password"], password):
            session["admin"] = username
            return redirect(url_for("admin_panel"))
        flash("Invalid username or password")
    return render_template("login.html")

# Admin panel
@app.route("/admin")
def admin_panel():
    if "admin" not in session:
        return redirect(url_for("login"))
    users = load_users()
    return render_template("admin.html", users=users)

# Add user
@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if "admin" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()
        if any(u["username"] == username for u in users):
            flash("User already exists")
        else:
            users.append({"username": username, "password": generate_password_hash(password)})
            save_users(users)
            flash("User added successfully")
            return redirect(url_for("admin_panel"))
    return render_template("add_user.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
