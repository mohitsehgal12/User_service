import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database setup
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

users = {}
user_id_counter = 1


@app.route('/user_service/users', methods=['POST'])
def create_user():
    global user_id_counter
    data = request.get_json()

    if 'username' in data and 'email' in data and 'password' in data:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (data['username'], data['email'], data['password']))
        conn.commit()

        cursor.execute("SELECT last_insert_rowid()")
        user_id = cursor.fetchone()[0]

        conn.close()

        return jsonify({"user_id": user_id}), 201
    else:
        return "Invalid user data", 400


@app.route('/user_service/users', methods=['GET'])
def list_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users_data = cursor.fetchall()
    conn.close()

    users_list = []
    for user in users_data:
        user_dict = {
            "user_id": user[0],
            "username": user[1],
            "email": user[2],
        }
        users_list.append(user_dict)

    return jsonify(users_list), 200


@app.route('/users/<int:user_id>', methods=['GET'])
def retrieve_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        user = {
            "user_id": user_data[0],
            "username": user_data[1],
            "email": user_data[2],
        }
        return jsonify(user), 200
    else:
        return "User not found", 404


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()

    if 'username' in data and 'email' in data and 'password' in data:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET username=?, email=?, password=? WHERE id=?",
                       (data['username'], data['email'], data['password'], user_id))
        conn.commit()
        conn.close()

        return jsonify({"user_id": user_id}), 200
    else:
        return "Invalid user data", 400


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return "", 204


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
