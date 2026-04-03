"""
Frontend Server - Serves HTML/CSS/JS and communicates with backend API
Run: python app.py (from part4/Frontend)
Note: Backend must be running on http://localhost:5000
"""

from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__, 
            static_folder='.',
            static_url_path='',
            template_folder='.')

# Allow CORS for API calls to backend
CORS(app)

# API BASE URL - Backend runs on port 5000
API_BASE_URL = 'http://localhost:5000/api/v1'

# Routes for serving static files

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    if filename.endswith('.html'):
        return send_from_directory('.', filename)
    elif filename.startswith('images/'):
        return send_from_directory('Images_Room', filename.replace('images/', ''))
    else:
        return send_from_directory('.', filename)

@app.context_processor
def inject_api_url():
    """Make API_BASE_URL available in templates"""
    return dict(API_BASE_URL=API_BASE_URL)

if __name__ == '__main__':
    print("=" * 60)
    print("HBnB Frontend Server")
    print("=" * 60)
    print(f"Frontend running on:  http://localhost:5001")
    print(f"Backend API at:       {API_BASE_URL}")
    print("=" * 60)
    print("\nMake sure backend is running:")
    print("  cd ../HBnB && python run.py")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5001)

