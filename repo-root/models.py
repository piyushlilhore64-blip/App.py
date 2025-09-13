from database import get_connection
from passlib.hash import bcrypt
import datetime

def add_user(username, password, time_limit):
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = bcrypt.hash(password)
    cursor.execute(
        "INSERT INTO users (username, password_hash, time_limit) VALUES (?, ?, ?)",
        (username, password_hash, time_limit)
    )
    conn.commit()
    conn.close()

def delete_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and bcrypt.verify(password, user["password_hash"]):
        return dict(user)
    return None

def set_login_time(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET login_start = CURRENT_TIMESTAMP WHERE username = ?", (username,)
    )
    conn.commit()
    conn.close()

def check_time_remaining(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT time_limit, login_start FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if not user or not user["login_start"]:
        return 0
    login_time = datetime.datetime.fromisoformat(user["login_start"])
    elapsed = (datetime.datetime.utcnow() - login_time).total_seconds() / 60  # minutes
    remaining = user["time_limit"] - elapsed
    return max(0, remaining)

def update_time(username, new_time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET time_limit = ? WHERE username = ?", (new_time, username)
    )
    conn.commit()
    conn.close()
