# HBnB - Part 4: Frontend Prototype

## Description

Part 4 is the frontend version of HBnB. It provides a simple browser interface for browsing places, viewing place details, logging in, and submitting reviews. The folder also includes a lightweight Flask app that serves example data and JWT-based login for local testing.

## Main Files

- `index.html` - main places listing page
- `place.html` - individual place details page
- `login.html` - login form
- `add_review.html` - review submission page
- `scripts.js` - frontend logic for authentication, fetching data, filtering, and UI updates
- `styles.css` - styling for the pages
- `app.py` - local Flask backend used by the frontend during development

## Features

- Browse available places
- Filter places by price
- Log in with a test user
- View place details and reviews
- Add a review when authenticated

## Run Locally

### 1. Install dependencies

```bash
pip install flask flask-jwt-extended flask-cors
```

### 2. Start the Flask app

```bash
python app.py
```

The app runs on `http://localhost:5000`.

## Usage Notes

- The frontend expects the backend to be available at `http://localhost:5000`.
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

# ✍️ Author

Holberton School — HBnB HBnB - Simple Web Client Project   
Team: 👥 - [David Roset](https://github.com/DevEchoFR)