from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import pyrebase
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Firebase configuration
firebaseConfig = {
    "apiKey": "AIzaSyD4dkOn3oGJyJmo06ghnPDAqwa-K5inD8I",
    "authDomain": "anytime-ecb4d.firebaseapp.com",
    "databaseURL": "https://anytime-ecb4d-default-rtdb.firebaseio.com",
    "projectId": "anytime-ecb4d",
    "storageBucket": "anytime-ecb4d.firebasestorage.app",
    "messagingSenderId": "351063324913",
    "appId": "1:351063324913:web:c8f96a365ceeef4b859150",
    "measurementId": "G-BZ4JHXSX8X"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# ------------------ Routes ------------------ #

@app.route('/')
def home():
    if not session.get("admin"):
        return redirect(url_for("login"))

    # Fetch all keys from Firebase
    keys_data = db.child("keys").get().val()
    total_keys = 0
    active_keys = 0
    expired_keys = 0
    now = datetime.now()

    if keys_data:
        total_keys = len(keys_data)
        for key, value in keys_data.items():
            valid_until = value.get("validity")
            if valid_until:
                # Parse stored date "DD-MM-YYYY HH:MM"
                dt = datetime.strptime(valid_until, "%d-%m-%Y %H:%M")
                if dt >= now and value.get("active", True):
                    active_keys += 1
                else:
                    expired_keys += 1

    return render_template('admin.html',
                           total_keys=total_keys,
                           active_keys=active_keys,
                           expired_keys=expired_keys,
                           keys_data=keys_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
