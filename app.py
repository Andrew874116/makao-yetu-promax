from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import pymysql
import pymysql.cursors
import bcrypt
import jwt
import datetime

app = Flask(__name__)
CORS(app)  # Allow all origins for now

app.config['SECRET_KEY'] = 'makao_yetu_secret_2026'

# Database config
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'mysql-andrewkifaru.alwaysdata.net'),
    'user': os.environ.get('DB_USER', 'andrewkifaru'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'andrewkifaru_makaoyetu'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'cursorclass': pymysql.cursors.DictCursor,
    'charset': 'utf8mb4'
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

@app.route('/')
def home():
    return jsonify({'message': 'Makao Yetu API is working! 🎉', 'status': 'alive'})

@app.route('/api/test')
def test():
    return jsonify({'message': 'Test endpoint works!'})

# ========== AUTH ENDPOINTS ==========
@app.route('/api/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                return jsonify({'error': 'Email already exists'}), 400
            cur.execute(
                "INSERT INTO users (username, email, password, phone) VALUES (%s, %s, %s, %s)",
                (username, email, hashed, phone)
            )
            db.commit()
            user_id = cur.lastrowid
        token = jwt.encode({'user_id': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)},
                           app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'message': 'Account created!', 'token': token, 'username': username, 'user_id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/signin', methods=['POST', 'OPTIONS'])
def signin():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
        token = jwt.encode({'user_id': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)},
                           app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'message': 'Login successful', 'token': token, 'username': user['username'], 'user_id': user['id']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# ========== PROPERTIES ==========
@app.route('/api/get_properties', methods=['GET', 'OPTIONS'])
def get_properties():
    if request.method == 'OPTIONS':
        return '', 200
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM properties LIMIT 20")
            props = cur.fetchall()
        return jsonify(props)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)