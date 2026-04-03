# HBnB - Part 4: Frontend Prototype

## Description

Part 4 is the frontend client for HBnB. It provides a browser interface for browsing places, viewing place details, logging in, submitting reviews, creating/editing places, and opening an admin dashboard.

Primary backend for this frontend: `part3/` API (`/api/v1/...`).

`part4/app.py` remains available as a lightweight local mock backend, but the recommended setup is to run Part 3 as the API/backend.

## Main Files

- `index.html` - main places listing page
- `place.html` - individual place details page
- `login.html` - login form
- `add_review.html` - review submission page
- `scripts.js` - frontend logic for authentication, fetching data, filtering, and UI updates
- `styles.css` - styling for the pages
- `app.py` - optional local mock Flask backend
- `create_edit_place.html` - create/edit listing form
- `admin.html` - admin dashboard page

## Features

- Browse available places
- Filter places by price
- Log in with a test user
- View place details and reviews
- Add a review when authenticated
- Password hashing for local users in the Flask app
- Rating validation (`1` to `5`) and duplicate-review protection per user/place
- Basic health endpoint: `GET /health`

## Run Locally

### 1. Install dependencies

```bash
pip install flask flask-jwt-extended flask-cors
```

### 2. Start the Flask app

```bash
# Recommended: run Part 3 API backend
cd ../part3
pip install -r requirements.txt
python run.py

# In a second terminal, run the Part 4 static frontend
cd ../part4
python -m http.server 3000 --bind 127.0.0.1
```

- Part 3 API runs on `http://localhost:5000`
- Part 4 frontend runs on `http://127.0.0.1:3000`

Optional alternative (mock backend):

```bash
python app.py
```

Optional environment variables:

- `JWT_SECRET_KEY` - custom JWT signing secret for local runs
- `JWT_EXPIRES_HOURS` - access token lifetime in hours (default: `24`)

## Usage Notes

- The frontend expects backend API endpoints under `http://localhost:5000/api/v1`.
- Example login credentials are printed when the Flask app starts.
- Data in `app.py` is stored in memory, so it resets when the server stops.

## Project Structure

```text
part4/
├── add_review.html
├── app.py
├── index.html
├── login.html
├── place.html
├── scripts.js
├── styles.css
└── images/
```

## ✍️ Author

Holberton School — HBnB HBnB - Simple Web Client Project
Team: 👥 - [David Roset](https://github.com/DevEchoFR)
