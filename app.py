from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")  # your admin panel HTMLfrom flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# API Login Endpoint
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password required"}), 400
    
    users = load_users()
    user = next((u for u in users if u["username"] == username), None)
    
    if user and check_password_hash(user["password"], password):
        return jsonify({"status": "success", "message": "Login successful"})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

# API to add a new user (Admin Only)
@app.route("/api/add_user", methods=["POST"])
def api_add_user():
    admin_key = request.headers.get("Admin-Key")
    if admin_key != os.environ.get("ADMIN_KEY"):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password required"}), 400

    users = load_users()
    if any(u["username"] == username for u in users):
        return jsonify({"status": "error", "message": "User already exists"}), 409

    users.append({"username": username, "password": generate_password_hash(password)})
    save_users(users)
    return jsonify({"status": "success", "message": "User added successfully"}), 201

# Health check
@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "server running"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    # Existing imports and setup stay the same
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import json, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")
USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# -------------------
# Login Endpoint
# -------------------
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password required"}), 400
    
    users = load_users()
    user = next((u for u in users if u["username"] == username), None)
    if user and check_password_hash(user["password"], password):
        return jsonify({"status": "success", "message": "Login successful"})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

# -------------------
# Add User (Admin)
# -------------------
@app.route("/api/add_user", methods=["POST"])
def api_add_user():
    admin_key = request.headers.get("Admin-Key")
    if admin_key != os.environ.get("ADMIN_KEY"):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password required"}), 400

    users = load_users()
    if any(u["username"] == username for u in users):
        return jsonify({"status": "error", "message": "User already exists"}), 409

    users.append({"username": username, "password": generate_password_hash(password)})
    save_users(users)
    return jsonify({"status": "success", "message": "User added successfully"}), 201

# -------------------
# List Users (Admin)
# -------------------
@app.route("/api/list_users", methods=["GET"])
def api_list_users():
    admin_key = request.headers.get("Admin-Key")
    if admin_key != os.environ.get("ADMIN_KEY"):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    users = load_users()
    usernames = [u["username"] for u in users]
    return jsonify({"status": "success", "users": usernames})

# -------------------
# Delete User (Admin)
# -------------------
@app.route("/api/delete_user", methods=["POST"])
def api_delete_user():
    admin_key = request.headers.get("Admin-Key")
    if admin_key != os.environ.get("ADMIN_KEY"):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    data = request.json
    username = data.get("username")
    users = load_users()
    if not any(u["username"] == username for u in users):
        return jsonify({"status": "error", "message": "User not found"}), 404

    users = [u for u in users if u["username"] != username]
    save_users(users)
    return jsonify({"status": "success", "message": f"User '{username}' deleted"})

# -------------------
# Health Check
# -------------------
@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "server running"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
