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

app = Flask(__name__)

# ─── CONFIG ───
app.config['JWT_SECRET_KEY'] = 'change-this-to-a-random-secret-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

CORS(app)          # Allow all origins (fine for dev)
jwt = JWTManager(app)

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
        'price': 85,
        'host': 'Alice',
        'location': 'Paris, France',
        'amenities': ['WiFi', 'Kitchen', 'Heating', 'Elevator']
    },
    {
        'id': '2',
        'name': 'Modern Loft near the Eiffel Tower',
        'description': 'Stylish open-plan loft just a 10-minute walk from the Eiffel Tower.',
        'price': 150,
        'host': 'Bob',
        'location': 'Paris, France',
        'amenities': ['WiFi', 'Air conditioning', 'Balcony', 'Dishwasher']
    },
    {
        'id': '3',
        'name': 'Charming Provence Farmhouse',
        'description': 'Peaceful stone farmhouse surrounded by lavender fields and olive trees.',
        'price': 220,
        'host': 'Alice',
        'location': 'Provence, France',
        'amenities': ['WiFi', 'Pool', 'Garden', 'Parking', 'BBQ']
    },
    {
        'id': '4',
        'name': 'Budget Room in the Latin Quarter',
        'description': 'Clean and comfortable private room in a shared apartment, great transport links.',
        'price': 45,
        'host': 'Bob',
        'location': 'Paris, France',
        'amenities': ['WiFi', 'Shared kitchen']
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


def make_place_image(title, location, primary, secondary, accent):
        svg = f"""
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 900' role='img' aria-label='{title}'>
            <defs>
                <linearGradient id='bg' x1='0%' y1='0%' x2='100%' y2='100%'>
                    <stop offset='0%' stop-color='{primary}' />
                    <stop offset='100%' stop-color='{secondary}' />
                </linearGradient>
                <radialGradient id='glow' cx='50%' cy='40%' r='70%'>
                    <stop offset='0%' stop-color='rgba(255,255,255,0.30)' />
                    <stop offset='100%' stop-color='rgba(255,255,255,0)' />
                </radialGradient>
            </defs>
            <rect width='1200' height='900' fill='url(#bg)' />
            <circle cx='920' cy='180' r='220' fill='url(#glow)' />
            <circle cx='190' cy='710' r='240' fill='rgba(255,255,255,0.08)' />
            <circle cx='980' cy='760' r='170' fill='rgba(255,255,255,0.10)' />
            <rect x='0' y='610' width='1200' height='290' fill='rgba(0,0,0,0.12)' />
            <path d='M0 645 C160 600, 290 700, 430 650 S730 600, 870 650 S1050 710, 1200 650 L1200 900 L0 900 Z' fill='rgba(255,255,255,0.10)' />
            <text x='72' y='760' fill='white' font-family='Georgia, serif' font-size='104' font-weight='700'>{title}</text>
            <text x='74' y='826' fill='rgba(255,255,255,0.88)' font-family='Arial, sans-serif' font-size='34' letter-spacing='4'>{location}</text>
            <rect x='72' y='92' rx='999' ry='999' width='220' height='58' fill='{accent}' fill-opacity='0.95' />
            <text x='112' y='132' fill='white' font-family='Arial, sans-serif' font-size='28' font-weight='700'>HBnB stay</text>
        </svg>
        """.strip()
        return f"data:image/svg+xml;charset=utf-8,{quote(svg, safe='')}"

# ─── ROUTES ───

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email    = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'message': 'Email and password are required.'}), 400
        'image': make_place_image('Montmartre', 'Paris', '#9C4F35', '#D88B5F', '#5D2418'),

    user = find_user(email)
    if not user or user['password'] != password:
        return jsonify({'message': 'Invalid email or password.'}), 401

    token = create_access_token(identity=user['id'])
    return jsonify({'access_token': token, 'user': {'id': user['id'], 'name': user['name']}}), 200


        'image': make_place_image('Eiffel Loft', 'Paris', '#1E3A5F', '#5B7FA8', '#D9A441'),
@app.route('/places', methods=['GET'])
def get_places():
    # Return all places (public endpoint — add @jwt_required() to restrict)
    return jsonify(places), 200


@app.route('/places/<place_id>', methods=['GET'])
def get_place(place_id):
    place = next((p for p in places if p['id'] == place_id), None)
        'image': make_place_image('Provence', 'France', '#6A4C93', '#A06CD5', '#F2C14E'),
    if not place:
        return jsonify({'message': 'Place not found.'}), 404

    place_reviews = [r for r in reviews if r['place_id'] == place_id]
    return jsonify({**place, 'reviews': place_reviews}), 200


@app.route('/reviews', methods=['POST'])
@jwt_required()
        'image': make_place_image('Latin Quarter', 'Paris', '#2B5876', '#4E4376', '#E07A5F'),
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
