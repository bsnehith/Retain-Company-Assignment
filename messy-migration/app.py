from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DB = 'users.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ------------------------ JSON API ROUTES ------------------------ #

@app.route('/api/users', methods=['GET'])
def get_all_users():
    conn = get_db()
    users = conn.execute("SELECT id, name, email FROM users").fetchall()
    conn.close()
    return jsonify([dict(u) for u in users]), 200

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db()
    user = conn.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user:
        return jsonify(dict(user)), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return jsonify({"error": "Missing fields"}), 400

    hashed_password = generate_password_hash(password)
    try:
        conn = get_db()
        conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                     (name, email, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"message": "User created"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409

@app.route('/api/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not all([name, email]):
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db()
    cur = conn.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, user_id))
    conn.commit()
    conn.close()

    if cur.rowcount == 0:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User updated"}), 200

@app.route('/api/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db()
    cur = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    if cur.rowcount == 0:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": f"User {user_id} deleted"}), 200

@app.route('/api/search', methods=['GET'])
def search_users():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Please provide a name"}), 400

    conn = get_db()
    users = conn.execute("SELECT id, name, email FROM users WHERE name LIKE ?", (f"%{name}%",)).fetchall()
    conn.close()
    return jsonify([dict(u) for u in users]), 200

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"error": "Missing credentials"}), 400

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return jsonify({"message": "Login successful", "user_id": user["id"]}), 200
    return jsonify({"error": "Invalid credentials"}), 401

# ------------------------ FRONTEND ROUTES ------------------------ #

@app.route('/')
def index():
    conn = get_db()
    users = conn.execute("SELECT id, name, email FROM users").fetchall()
    conn.close()
    return render_template('index.html', users=users)

@app.route('/add', methods=['GET', 'POST'])
def add_user_page():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        if not all([name, email, password]):
            return "Missing fields", 400

        try:
            conn = get_db()
            conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                         (name, email, generate_password_hash(password)))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            return "Email already exists", 409

    return render_template('add_user.html')

@app.route('/delete/<int:user_id>')
def delete_user_page(user_id):
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            return f"Welcome, {user['name']}!"
        else:
            return "Invalid credentials", 401

    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)
