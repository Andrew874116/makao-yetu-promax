from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import jwt
import datetime
import os
import uuid
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from functools import wraps
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
socketio = SocketIO(app, cors_allowed_origins="*")

# ========== CONFIG ==========
app.config['SECRET_KEY'] = 'makao_yetu_secret_2026'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp', 'pdf', 'mp4', 'mov', 'avi'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Email config – CHANGE TO YOUR REAL CREDENTIALS
app.config['EMAIL_ADDRESS'] = 'andrewmuthengi80@gmail.com'
app.config['EMAIL_PASSWORD'] = 'BMAndrew5170'

# Google OAuth – CHANGE TO YOUR CLIENT ID
app.config['GOOGLE_CLIENT_ID'] = '71183583717-hfl3g7nmhm40p8ifcm4029oiiv4t99tj.apps.googleusercontent.com'

# Cloudinary – CHANGE TO YOUR CREDENTIALS
cloudinary.config(
    cloud_name = 'dtbdualnw',
    api_key = '532688159716588',
    api_secret = '*********************************'
)

# Database
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'makao_yetu'),
    'cursorclass': pymysql.cursors.DictCursor,
    'charset': 'utf8mb4'
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user_id = data['user_id']
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['EMAIL_ADDRESS']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(app.config['EMAIL_ADDRESS'], app.config['EMAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

def generate_otp():
    return str(random.randint(100000, 999999))

# ========== AUTH ==========
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    phone = data.get('phone', '').strip()

    if not all([username, email, password, phone]):
        return jsonify({'error': 'All fields required'}), 400

    hashed = generate_password_hash(password)
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                return jsonify({'error': 'Email already registered'}), 409
            cur.execute(
                "INSERT INTO users (username, email, password, phone, is_verified, is_admin) VALUES (%s,%s,%s,%s,0,0)",
                (username, email, hashed, phone)
            )
            db.commit()
            user_id = cur.lastrowid
        token = jwt.encode({'user_id': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)},
                           app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'message': 'Account created', 'token': token, 'username': username, 'user_id': user_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/signin', methods=['POST'])
def signin():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        token = jwt.encode({'user_id': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)},
                           app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'username': user['username'],
            'user_id': user['id'],
            'is_verified': user.get('is_verified', 0),
            'is_admin': user.get('is_admin', 0)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/google_auth', methods=['POST'])
def google_auth():
    try:
        credential = request.json.get('credential')
        info = id_token.verify_oauth2_token(credential, google_requests.Request(), app.config['GOOGLE_CLIENT_ID'])
        email = info['email']
        name = info.get('name', email.split('@')[0])
        db = get_db()
        with db.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            if user:
                user_id = user['id']
                username = user['username']
            else:
                cur.execute("INSERT INTO users (username, email, password, phone, is_verified, is_admin) VALUES (%s,%s,'', '',0,0)",
                            (name, email))
                db.commit()
                user_id = cur.lastrowid
                username = name
        token = jwt.encode({'user_id': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)},
                           app.config['SECRET_KEY'], algorithm='HS256')
        db.close()
        return jsonify({'message': 'Google login successful', 'token': token, 'username': username, 'user_id': user_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 401

# ========== PASSWORD RESET (OTP) ==========
@app.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if not cur.fetchone():
            return jsonify({'message': 'If email exists, OTP sent'}), 200
        otp = generate_otp()
        expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        cur.execute("INSERT INTO password_resets (email, otp, expires_at) VALUES (%s,%s,%s)", (email, otp, expires))
        db.commit()
    body = f'<h2>Your OTP: {otp}</h2><p>Valid for 15 minutes.</p>'
    send_email(email, 'Password Reset OTP', body)
    return jsonify({'message': 'OTP sent'}), 200

@app.route('/api/verify_otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM password_resets WHERE email=%s AND otp=%s AND used=0 AND expires_at > NOW()", (email, otp))
        row = cur.fetchone()
    db.close()
    if not row:
        return jsonify({'error': 'Invalid or expired OTP'}), 400
    return jsonify({'message': 'OTP verified'}), 200

@app.route('/api/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM password_resets WHERE email=%s AND otp=%s AND used=0 AND expires_at > NOW()", (email, otp))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'Invalid or expired OTP'}), 400
        hashed = generate_password_hash(new_password)
        cur.execute("UPDATE users SET password = %s WHERE email = %s", (hashed, email))
        cur.execute("UPDATE password_resets SET used = 1 WHERE id = %s", (row['id'],))
        db.commit()
    db.close()
    return jsonify({'message': 'Password reset successfully'}), 200

# ========== PROPERTIES (SIMPLIFIED) ==========
@app.route('/api/add_property', methods=['POST'])
@token_required
def add_property():
    # Simplified – just store basic fields, no Cloudinary for brevity
    title = request.form.get('title')
    location = request.form.get('location')
    price = request.form.get('price')
    prop_type = request.form.get('prop_type', 'rent')
    description = request.form.get('description', '')
    image = None
    if 'image' in request.files:
        f = request.files['image']
        if f and allowed_file(f.filename):
            ext = f.filename.rsplit('.', 1)[1].lower()
            image = f"{uuid.uuid4().hex}.{ext}"
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], image))
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""INSERT INTO properties (title, location, price, prop_type, description, image, user_id)
                           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        (title, location, price, prop_type, description, image, request.user_id))
            db.commit()
            prop_id = cur.lastrowid
        return jsonify({'message': 'Property listed', 'property_id': prop_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/get_properties', methods=['GET'])
def get_properties():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT p.*, u.username as agent_name FROM properties p JOIN users u ON p.user_id = u.id WHERE p.is_available=1 ORDER BY p.created_at DESC")
            props = cur.fetchall()
        return jsonify(props)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/get_property/<int:pid>', methods=['GET'])
def get_property(pid):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("UPDATE properties SET views = views + 1 WHERE id = %s", (pid,))
            db.commit()
            cur.execute("SELECT p.*, u.username as agent_name, u.phone as agent_phone, u.email as agent_email FROM properties p JOIN users u ON p.user_id = u.id WHERE p.id=%s", (pid,))
            prop = cur.fetchone()
        return jsonify(prop) if prop else jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# ========== FAVORITES ==========
@app.route('/api/favorites', methods=['GET'])
@token_required
def get_favorites():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT p.* FROM properties p JOIN favorites f ON p.id=f.property_id WHERE f.user_id=%s", (request.user_id,))
            favs = cur.fetchall()
        return jsonify(favs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/favorites/<int:pid>', methods=['POST'])
@token_required
def add_favorite(pid):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("INSERT IGNORE INTO favorites (user_id, property_id) VALUES (%s,%s)", (request.user_id, pid))
            db.commit()
        return jsonify({'message': 'Added'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/favorites/<int:pid>', methods=['DELETE'])
@token_required
def remove_favorite(pid):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM favorites WHERE user_id=%s AND property_id=%s", (request.user_id, pid))
            db.commit()
        return jsonify({'message': 'Removed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# ========== BOOKINGS ==========
@app.route('/api/book_property', methods=['POST'])
@token_required
def book_property():
    data = request.json
    pid = data.get('property_id')
    amount = data.get('amount')
    phone = data.get('phone')
    if not pid or not amount:
        return jsonify({'error': 'Missing fields'}), 400
    ref = f"MKY{uuid.uuid4().hex[:8].upper()}"
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("INSERT INTO bookings (user_id, property_id, amount, phone, mpesa_ref, status) VALUES (%s,%s,%s,%s,%s,'confirmed')",
                        (request.user_id, pid, amount, phone, ref))
            db.commit()
            bid = cur.lastrowid
        return jsonify({'message': 'Booking confirmed', 'booking_id': bid, 'mpesa_ref': ref})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/my_bookings', methods=['GET'])
@token_required
def my_bookings():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT b.*, p.title as property_title FROM bookings b JOIN properties p ON b.property_id=p.id WHERE b.user_id=%s", (request.user_id,))
            bookings = cur.fetchall()
        return jsonify(bookings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# ========== CHAT (SIMPLIFIED) ==========
active_chat_users = {}
@socketio.on('join_chat')
def join_chat(data):
    room = f"chat_{min(data['user_id'], data['other_user_id'])}_{max(data['user_id'], data['other_user_id'])}"
    join_room(room)
    active_chat_users[request.sid] = data['user_id']

@socketio.on('send_message')
def send_message(data):
    room = f"chat_{min(data['sender_id'], data['receiver_id'])}_{max(data['sender_id'], data['receiver_id'])}"
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("INSERT INTO chat_messages (sender_id, receiver_id, property_id, message) VALUES (%s,%s,%s,%s)",
                        (data['sender_id'], data['receiver_id'], data.get('property_id'), data['message']))
            db.commit()
            msg_id = cur.lastrowid
        emit('new_message', {'id': msg_id, 'sender_id': data['sender_id'], 'message': data['message']}, to=room)
    finally:
        db.close()

@app.route('/api/my_conversations', methods=['GET'])
@token_required
def my_conversations():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT CASE WHEN sender_id=%s THEN receiver_id ELSE sender_id END as other_id,
                       (SELECT username FROM users WHERE id=other_id) as other_name,
                       (SELECT message FROM chat_messages WHERE (sender_id=%s AND receiver_id=other_id) OR (sender_id=other_id AND receiver_id=%s) ORDER BY created_at DESC LIMIT 1) as last_message
                FROM chat_messages WHERE sender_id=%s OR receiver_id=%s
            """, (request.user_id, request.user_id, request.user_id, request.user_id, request.user_id))
            convos = cur.fetchall()
        return jsonify(convos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/chat_messages/<int:other_id>', methods=['GET'])
@token_required
def chat_messages(other_id):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT * FROM chat_messages WHERE (sender_id=%s AND receiver_id=%s) OR (sender_id=%s AND receiver_id=%s) ORDER BY created_at ASC
            """, (request.user_id, other_id, other_id, request.user_id))
            msgs = cur.fetchall()
        return jsonify(msgs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# ========== STATIC FILES ==========
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ========== RUN ==========
if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)