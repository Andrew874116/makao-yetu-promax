from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({'message': 'Makao Yetu API is working! 🎉', 'status': 'alive'})

@app.route('/api/test')
def test():
    return jsonify({'message': 'Test endpoint works!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)