from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # change this to something strong
db_file = "users.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(db_file)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    """)
    # Create default admin if none exists
    admin = conn.execute("SELECT * FROM admins").fetchone()
    if not admin:
        default_pw = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
        conn.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", ("admin", default_pw))
    conn.commit()
    conn.close()

init_db()

# Admin login page
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect(db_file)
        admin = conn.execute("SELECT password_hash FROM admins WHERE username=?", (username,)).fetchone()
        conn.close()

        if admin and bcrypt.checkpw(password.encode(), admin[0]):
            session['admin'] = username
            return redirect(url_for('admin_panel'))
        return "Invalid admin credentials", 401

    return '''
    <form method="POST">
        <input name="username" placeholder="Admin Username">
        <input type="password" name="password" placeholder="Password">
        <button type="submit">Login</button>
    </form>
    '''

# Admin panel (protected)
@app.route('/')
def admin_panel():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    return render_template('index.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# Rest of user management routes remain same
# /users, /register, /delete/<id>, /login
