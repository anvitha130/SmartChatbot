# api.py
# Flask API with JWT-based login/register and protected endpoint
import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

# Config
DB_NAME = os.getenv("DB_NAME", "data.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_change_me")  # set in .env for production

# --- Database helpers ---
def init_db():
    """Create DB and users table if not exists."""
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def add_user(username, password, role="user"):
    pwd_hash = generate_password_hash(password)
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, pwd_hash, role))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_user(username):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
    return row  # None or tuple

# --- JWT helpers ---
def create_token(username, role):
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    # PyJWT may return bytes for older versions; ensure string
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Token is missing"}), 401
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except Exception as e:
            return jsonify({"message": "Token is invalid", "error": str(e)}), 401
        return f(*args, **kwargs)
    return decorated

# --- Routes expected by tests ---
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400
    ok = add_user(username, password, role="user")
    if ok:
        return jsonify({"message": "User registered"}), 201
    else:
        return jsonify({"error": "User already exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400

    row = get_user(username)
    if row and check_password_hash(row[2], password):
        token = create_token(username, row[3])
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/protected", methods=["GET"])
@token_required
def protected():
    user = request.user
    return jsonify({"message": f"Hello {user.get('username')}, you accessed protected endpoint", "user": user}), 200

# optional test endpoint
@app.route("/secure_data", methods=["GET"])
@token_required
def secure_data():
    return jsonify({"data": "This is protected data accessible after login!"})

# Add a health check route
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# Run server
if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    # create default users (do not override existing)
    add_user("testuser", "testpass", "user")
    add_user("admin", "adminpass", "admin")
    print("✅ Default users ensured in DB")
    print("🚀 API running on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
