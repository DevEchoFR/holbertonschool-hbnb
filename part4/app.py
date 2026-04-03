"""
app.py — HBnB Flask Backend
Run: python app.py
Requires: pip install flask flask-jwt-extended flask-cors
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from datetime import timedelta
import uuid
from urllib.parse import quote
import os

app = Flask(__name__, static_folder='Images_Room', static_url_path='/images')

# ─── CONFIG ───
app.config['JWT_SECRET_KEY'] = 'change-this-to-a-random-secret-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

CORS(app)          # Allow all origins (fine for dev)
jwt = JWTManager(app)

IMAGE_BASE_URL = 'http://localhost:5000/images'

# ─── IN-MEMORY DATA STORE ───
# Replace with a real database (SQLite, PostgreSQL, etc.) for production.

users = [
    {
        'id': '1',
        'email': 'alice@example.com',
        'password': 'password123',   # NEVER store plain text in production — use bcrypt
        'name': 'Alice'
    },
    {
        'id': '2',
        'email': 'bob@example.com',
        'password': 'password123',
        'name': 'Bob'
    }
]

places = [
    {
        'id': '1',
        'name': 'Cosy Studio in Montmartre',
        'description': 'A bright studio apartment in the heart of Montmartre with stunning views of Sacré-Cœur.',
        'price': 175,
        'host': 'Alice',
        'location': 'Paris, France',
        'image': f'{IMAGE_BASE_URL}/Cosy Studio in Montmartre.jpg',
        'amenities': ['WiFi', 'Air conditioning', 'Heating', 'Elevator', 'Balcony', 'Kitchen', 'Dishwasher']
    },
    {
        'id': '2',
        'name': 'Modern Loft near the Eiffel Tower',
        'description': 'Stylish open-plan loft just a 10-minute walk from the Eiffel Tower.',
        'price': 125,
        'host': 'Bob',
        'location': 'Paris, France',
        'image': f'{IMAGE_BASE_URL}/Modern Loft near the Eiffel Tower.jpg',
        'amenities': ['WiFi', 'Air conditioning', 'Heating', 'Balcony',]
    },
    {
        'id': '3',
        'name': 'Charming Provence Farmhouse',
        'description': 'Peaceful stone farmhouse surrounded by lavender fields and olive trees.',
        'price': 225,
        'host': 'Alice',
        'location': 'Provence, France',
        'image': f'{IMAGE_BASE_URL}/Charming Provence Farmhouse.jpg',
        'amenities': ['WiFi', 'Air conditioning', 'Heating', 'Pool', 'Garden', 'Parking', 'BBQ', 'Dishwasher']
    },
    {
        'id': '4',
        'name': 'Budget Room in the Latin Quarter',
        'description': 'Clean and comfortable private room in a shared apartment, great transport links.',
        'price': 75,
        'host': 'Bob',
        'location': 'Paris, France',
        'image': f'{IMAGE_BASE_URL}/Budget Room in the Latin Quarter.jpg',
        'amenities': ['WiFi', 'Air conditioning', 'Heating', 'Shared kitchen']
    }
]

reviews = [
    {'id': '1', 'place_id': '1', 'user': 'Bob',   'text': 'Absolutely lovely stay! The neighbourhood is full of charm.', 'rating': 5},
    {'id': '2', 'place_id': '1', 'user': 'Carol', 'text': 'Clean, well-located and the host was very responsive.', 'rating': 4},
    {'id': '3', 'place_id': '2', 'user': 'Alice', 'text': 'Great loft, very spacious. Would definitely come back.', 'rating': 5},
]

# ─── HELPER ───

def find_user(email):
    return next((u for u in users if u['email'] == email), None)

# ─── ROUTES ───

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email    = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'message': 'Email and password are required.'}), 400

    user = find_user(email)
    if not user or user['password'] != password:
        return jsonify({'message': 'Invalid email or password.'}), 401

    token = create_access_token(identity=user['id'])
    return jsonify({'access_token': token, 'user': {'id': user['id'], 'name': user['name']}}), 200


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(silent=True) or {}
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'message': 'Name, email, and password are required.'}), 400

    if find_user(email):
        return jsonify({'message': 'Email already registered.'}), 409

    new_user = {
        'id': str(uuid.uuid4()),
        'name': name,
        'email': email,
        'password': password
    }
    users.append(new_user)

    token = create_access_token(identity=new_user['id'])
    return jsonify({'access_token': token, 'user': {'id': new_user['id'], 'name': new_user['name']}}), 201


@app.route('/places', methods=['GET'])
def get_places():
    # Return all places (public endpoint — add @jwt_required() to restrict)
    return jsonify(places), 200


@app.route('/places/<place_id>', methods=['GET'])
def get_place(place_id):
    place = next((p for p in places if p['id'] == place_id), None)
    if not place:
        return jsonify({'message': 'Place not found.'}), 404

    place_reviews = [r for r in reviews if r['place_id'] == place_id]
    return jsonify({**place, 'reviews': place_reviews}), 200


@app.route('/reviews', methods=['POST'])
@jwt_required()
def add_review():
    user_id = get_jwt_identity()
    user    = next((u for u in users if u['id'] == user_id), None)
    data    = request.get_json(silent=True) or {}

    place_id = data.get('place_id', '').strip()
    text     = data.get('text', '').strip()
    rating   = data.get('rating', 0)

    if not place_id or not text:
        return jsonify({'message': 'place_id and text are required.'}), 400

    if not any(p['id'] == place_id for p in places):
        return jsonify({'message': 'Place not found.'}), 404

    review = {
        'id':       str(uuid.uuid4()),
        'place_id': place_id,
        'user':     user['name'] if user else 'Anonymous',
        'text':     text,
        'rating':   int(rating)
    }
    reviews.append(review)

    return jsonify({'message': 'Review added.', 'review': review}), 201


# ─── RUN ───
if __name__ == '__main__':
    print("✅ HBnB backend running at http://localhost:5000")
    print("   Test credentials: alice@example.com / password123")
    app.run(debug=True, port=5000)
