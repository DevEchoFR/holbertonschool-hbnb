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
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='Images_Room', static_url_path='/images')

# ─── CONFIG ───
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'change-this-to-a-random-secret-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=int(os.environ.get('JWT_EXPIRES_HOURS', '24')))

CORS(app)          # Allow all origins (fine for dev)
jwt = JWTManager(app)

IMAGE_BASE_URL = 'http://localhost:5000/images'

# ─── IN-MEMORY DATA STORE ───
# Replace with a real database (SQLite, PostgreSQL, etc.) for production.

users = [
    {
        'id': '1',
        'email': 'alice@example.com',
        'password': generate_password_hash('AliceDemo!2026'),
        'name': 'Alice',
        'is_admin': True
    },
    {
        'id': '2',
        'email': 'bob@example.com',
        'password': generate_password_hash('BobDemo!2026'),
        'name': 'Bob',
        'is_admin': False
    }
]

places = [
    {
        'id': '1',
        'name': 'Cozy Studio in Lisbon',
        'description': 'A bright studio in a lively district with scenic viewpoints and cafes nearby.',
        'price': 175,
        'host': 'Alice',
        'owner_id': '1',
        'location': 'Lisbon, Portugal',
        'image': f'{IMAGE_BASE_URL}/Cosy Studio in Montmartre.jpg',
        'amenities': ['WiFi', 'Air conditioning', 'Heating', 'Elevator', 'Balcony', 'Kitchen', 'Dishwasher']
    },
    {
        'id': '2',
        'name': 'Modern Loft in Barcelona',
        'description': 'A stylish open-plan loft close to restaurants, galleries, and waterfront walks.',
        'price': 125,
        'host': 'Bob',
        'owner_id': '2',
        'location': 'Barcelona, Spain',
        'image': f'{IMAGE_BASE_URL}/Modern Loft near the Eiffel Tower.jpg',
        'amenities': ['WiFi', 'Air conditioning', 'Heating', 'Balcony',]
    },
    {
        'id': '3',
        'name': 'Charming Countryside House',
        'description': 'A peaceful countryside house surrounded by greenery, ideal for a relaxing escape.',
        'price': 225,
        'host': 'Alice',
        'owner_id': '1',
        'location': 'Tuscany, Italy',
        'image': f'{IMAGE_BASE_URL}/Charming Provence Farmhouse.jpg',
        'amenities': ['WiFi', 'Air conditioning', 'Heating', 'Pool', 'Garden', 'Parking', 'BBQ', 'Dishwasher']
    },
    {
        'id': '4',
        'name': 'Budget Room in Prague Center',
        'description': 'A clean and comfortable private room with great public transport connections.',
        'price': 75,
        'host': 'Bob',
        'owner_id': '2',
        'location': 'Prague, Czech Republic',
        'image': f'{IMAGE_BASE_URL}/Budget Room in the Latin Quarter.jpg',
        'amenities': ['WiFi', 'Air conditioning', 'Heating', 'Shared kitchen']
    }
]

reviews = [
    {'id': '1', 'place_id': '1', 'user_id': '2', 'user': 'Bob', 'text': 'Absolutely lovely stay! The neighbourhood is full of charm.', 'rating': 5},
    {'id': '2', 'place_id': '1', 'user_id': '2', 'user': 'Bob', 'text': 'Clean, well-located and the host was very responsive.', 'rating': 4},
    {'id': '3', 'place_id': '2', 'user_id': '1', 'user': 'Alice', 'text': 'Great loft, very spacious. Would definitely come back.', 'rating': 5},
]

# ─── HELPER ───

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

def find_user(email):
    normalized_email = email.strip().lower()
    return next((u for u in users if u['email'].lower() == normalized_email), None)


def sanitize_user(user):
    return {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'is_admin': bool(user.get('is_admin', False))
    }


def is_valid_email(email):
    return bool(EMAIL_REGEX.match(email))


def get_user_by_id(user_id):
    return next((u for u in users if u['id'] == user_id), None)


def parse_place_payload(payload):
    name = payload.get('name', '').strip()
    description = payload.get('description', '').strip()
    location = payload.get('location', '').strip()
    amenities = payload.get('amenities', [])

    if not name or not description or not location:
        return None, 'name, description, and location are required.'

    if not isinstance(amenities, list):
        return None, 'amenities must be a list of strings.'

    try:
        price = int(payload.get('price', 0))
    except (TypeError, ValueError):
        return None, 'price must be a valid number.'

    if price <= 0:
        return None, 'price must be greater than zero.'

    clean_amenities = [str(item).strip() for item in amenities if str(item).strip()]

    return {
        'name': name,
        'description': description,
        'location': location,
        'price': price,
        'amenities': clean_amenities
    }, None

# ─── ROUTES ───

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email    = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'message': 'Email and password are required.'}), 400

    user = find_user(email)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid email or password.'}), 401

    token = create_access_token(identity=user['id'])
    return jsonify({'access_token': token, 'user': sanitize_user(user)}), 200


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(silent=True) or {}
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'message': 'Name, email, and password are required.'}), 400

    if not is_valid_email(email):
        return jsonify({'message': 'Please provide a valid email address.'}), 400

    if len(password) < 8:
        return jsonify({'message': 'Password must be at least 8 characters long.'}), 400

    if find_user(email):
        return jsonify({'message': 'Email already registered.'}), 409

    new_user = {
        'id': str(uuid.uuid4()),
        'name': name,
        'email': email,
        'password': generate_password_hash(password)
    }
    users.append(new_user)

    token = create_access_token(identity=new_user['id'])
    return jsonify({'access_token': token, 'user': sanitize_user(new_user)}), 201


@app.route('/places', methods=['GET'])
def get_places():
    # Return all places (public endpoint — add @jwt_required() to restrict)
    return jsonify(places), 200


@app.route('/places', methods=['POST'])
@jwt_required()
def create_place():
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)
    data = request.get_json(silent=True) or {}

    place_payload, error = parse_place_payload(data)
    if error:
        return jsonify({'message': error}), 400

    place = {
        'id': str(uuid.uuid4()),
        'name': place_payload['name'],
        'description': place_payload['description'],
        'price': place_payload['price'],
        'host': user['name'] if user else 'Unknown host',
        'owner_id': user_id,
        'location': place_payload['location'],
        'image': f"{IMAGE_BASE_URL}/Cosy Studio in Montmartre.jpg",
        'amenities': place_payload['amenities']
    }
    places.append(place)
    return jsonify(place), 201


@app.route('/places/<place_id>', methods=['GET'])
def get_place(place_id):
    place = next((p for p in places if p['id'] == place_id), None)
    if not place:
        return jsonify({'message': 'Place not found.'}), 404

    place_reviews = [r for r in reviews if r['place_id'] == place_id]
    return jsonify({**place, 'reviews': place_reviews}), 200


@app.route('/places/<place_id>', methods=['PUT'])
@jwt_required()
def update_place(place_id):
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)
    place = next((p for p in places if p['id'] == place_id), None)
    if not place:
        return jsonify({'message': 'Place not found.'}), 404

    is_owner = place.get('owner_id') == user_id
    is_admin = bool(user and user.get('is_admin'))
    if not is_owner and not is_admin:
        return jsonify({'message': 'You are not allowed to edit this place.'}), 403

    data = request.get_json(silent=True) or {}
    place_payload, error = parse_place_payload(data)
    if error:
        return jsonify({'message': error}), 400

    place['name'] = place_payload['name']
    place['description'] = place_payload['description']
    place['price'] = place_payload['price']
    place['location'] = place_payload['location']
    place['amenities'] = place_payload['amenities']

    return jsonify(place), 200


@app.route('/reviews', methods=['POST'])
@jwt_required()
def add_review():
    user_id = get_jwt_identity()
    user    = next((u for u in users if u['id'] == user_id), None)
    data    = request.get_json(silent=True) or {}

    place_id = data.get('place_id', '').strip()
    text     = data.get('text', '').strip()
    rating_raw = data.get('rating', 0)

    if not place_id or not text:
        return jsonify({'message': 'place_id and text are required.'}), 400

    if not any(p['id'] == place_id for p in places):
        return jsonify({'message': 'Place not found.'}), 404

    try:
        rating = int(rating_raw)
    except (TypeError, ValueError):
        return jsonify({'message': 'rating must be an integer between 1 and 5.'}), 400

    if rating < 1 or rating > 5:
        return jsonify({'message': 'rating must be an integer between 1 and 5.'}), 400

    if any(r.get('place_id') == place_id and r.get('user_id') == user_id for r in reviews):
        return jsonify({'message': 'You already reviewed this place.'}), 409

    review = {
        'id':       str(uuid.uuid4()),
        'place_id': place_id,
        'user_id':  user_id,
        'user':     user['name'] if user else 'Anonymous',
        'text':     text,
        'rating':   rating
    }
    reviews.append(review)

    return jsonify({'message': 'Review added.', 'review': review}), 201


@app.route('/admin/overview', methods=['GET'])
@jwt_required()
def admin_overview():
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)
    if not user or not user.get('is_admin'):
        return jsonify({'message': 'Admin access required.'}), 403

    return jsonify({
        'stats': {
            'users': len(users),
            'places': len(places),
            'reviews': len(reviews)
        },
        'users': [sanitize_user(u) for u in users],
        'places': places,
        'reviews': reviews
    }), 200


# ─── RUN ───
if __name__ == '__main__':
    print("✅ HBnB backend running at http://localhost:5000")
    print("   Test credentials: alice@example.com / AliceDemo!2026")
    app.run(debug=True, port=5000)
