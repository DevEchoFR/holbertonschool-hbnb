/* ============================================================
   scripts.js — HBnB Frontend Logic
   ============================================================ */

const API_BASE = 'http://localhost:5000';   // ← change this to your server URL

/* ─── UTILITIES ─── */

function getCookie(name) {
  return document.cookie.split('; ')
    .find(row => row.startsWith(name + '='))
    ?.split('=')[1];
}

function setCookie(name, value, days = 7) {
  const expires = new Date(Date.now() + days * 86400000).toUTCString();
  document.cookie = `${name}=${value}; expires=${expires}; path=/`;
}

function deleteCookie(name) {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/`;
}

function getQueryParam(key) {
  return new URLSearchParams(window.location.search).get(key);
}

function showToast(message, type = '') {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.className = 'toast ' + type;
  // Trigger reflow so transition replays
  void toast.offsetWidth;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3500);
}

function setButtonLoading(btn, loading) {
  if (!btn) return;
  if (loading) {
    btn.dataset.originalText = btn.textContent;
    btn.textContent = 'Please wait…';
    btn.disabled = true;
  } else {
    btn.textContent = btn.dataset.originalText || btn.textContent;
    btn.disabled = false;
  }
}

/* ─── AUTH HELPERS ─── */

function getToken() {
  return getCookie('token');
}

function checkAuth() {
  const token = getToken();
  if (!token) {
    window.location.href = 'login.html';
  }
  return token;
}

/** Update header login button based on auth state */
function syncAuthUI() {
  const token = getToken();
  const btn = document.getElementById('header-login-btn');
  const navLink = document.getElementById('nav-login-link');

  if (token && btn) {
    btn.textContent = 'Logout';
    btn.href = '#';
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      deleteCookie('token');
      window.location.href = 'login.html';
    });
  }
  if (token && navLink) {
    navLink.textContent = 'Logout';
    navLink.href = '#';
    navLink.addEventListener('click', (e) => {
      e.preventDefault();
      deleteCookie('token');
      window.location.href = 'login.html';
    });
  }
}

/* ============================================================
   PAGE: LOGIN
   ============================================================ */

function initLoginPage() {
  const form = document.getElementById('login-form');
  if (!form) return;

  // Redirect if already logged in
  if (getToken()) {
    window.location.href = 'index.html';
    return;
  }

  form.addEventListener('submit', handleLogin);
}

async function handleLogin(e) {
  e.preventDefault();

  const email    = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const btn      = document.getElementById('login-btn');

  if (!email || !password) {
    showToast('Please fill in all fields.', 'error');
    return;
  }

  setButtonLoading(btn, true);

  try {
    const response = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (response.ok) {
      const data = await response.json();
      setCookie('token', data.access_token);
      showToast('Logged in! Redirecting…', 'success');
      setTimeout(() => { window.location.href = 'index.html'; }, 800);
    } else {
      const err = await response.json().catch(() => ({}));
      showToast(err.message || 'Login failed. Check your credentials.', 'error');
      setButtonLoading(btn, false);
    }
  } catch (error) {
    showToast('Cannot reach the server. Is the backend running?', 'error');
    setButtonLoading(btn, false);
  }
}

/* ============================================================
   PAGE: INDEX (PLACES LIST)
   ============================================================ */

let allPlaces = [];

function initIndexPage() {
  const container = document.getElementById('places-list');
  if (!container) return;

  const token = getToken();
  fetchPlaces(token);

  const filter = document.getElementById('price-filter');
  if (filter) {
    filter.addEventListener('change', applyPriceFilter);
  }
}

async function fetchPlaces(token) {
  try {
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_BASE}/places`, { headers });

    if (response.status === 401) {
      // Show places anyway if API allows, or redirect
      showToast('Sign in to see all places.', '');
    }

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    allPlaces = await response.json();
    displayPlaces(allPlaces);
  } catch (error) {
    console.error('fetchPlaces:', error);
    document.getElementById('places-list').innerHTML = `
      <div class="empty-state" style="grid-column:1/-1">
        <div class="icon">🔌</div>
        <h3>Cannot load places</h3>
        <p>Make sure the backend is running at <strong>${API_BASE}</strong></p>
      </div>`;
  }
}

function displayPlaces(places) {
  const container = document.getElementById('places-list');
  const countEl   = document.getElementById('result-count');

  if (!places.length) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1">
        <div class="icon">🏠</div>
        <h3>No places found</h3>
        <p>Try adjusting your filter.</p>
      </div>`;
    if (countEl) countEl.textContent = '';
    return;
  }

  container.innerHTML = '';
  if (countEl) countEl.textContent = `${places.length} place${places.length !== 1 ? 's' : ''}`;

  places.forEach(place => {
    const div = document.createElement('div');
    div.className = 'place-card';
    div.dataset.price = place.price;
    const placeImage = getPlaceImage(place);
    const placeUrl = `place.html?id=${encodeURIComponent(place.id)}`;
    const placeLocation = place.location || 'Stay somewhere special';
    const amenityPreview = (place.amenities || []).map(a => amenityTag(a)).join('');

    div.innerHTML = `
      <a class="place-card-media" href="${placeUrl}" aria-label="View ${escapeHtml(place.name)}">
        <img src="${placeImage}" alt="${escapeHtml(place.name)}" loading="lazy" />
        <span class="price-pill">€${place.price}<small>/ night</small></span>
      </a>
      <div class="place-card-body">
        <div class="place-card-topline">
          <span class="place-location">${escapeHtml(placeLocation)}</span>
          <span class="place-host">Hosted by ${escapeHtml(place.host || 'HBnB')}</span>
        </div>
        <h3><a href="${placeUrl}">${escapeHtml(place.name)}</a></h3>
        <p class="place-card-description">
          ${escapeHtml(place.description || '')}
        </p>
        ${amenityPreview ? `<div class="amenities-list place-card-amenities">${amenityPreview}</div>` : ''}
        <div class="place-card-actions">
          <a href="${placeUrl}">
            <button class="details-button">Explore stay →</button>
          </a>
        </div>
      </div>
    `;

    container.appendChild(div);
  });
}

function applyPriceFilter() {
  const maxPrice = document.getElementById('price-filter').value;
  const cards    = document.querySelectorAll('.place-card');
  let visible    = 0;

  cards.forEach(card => {
    const price = parseFloat(card.dataset.price);
    const show  = maxPrice === 'All' || price <= parseFloat(maxPrice);
    card.style.display = show ? '' : 'none';
    if (show) visible++;
  });

  const countEl = document.getElementById('result-count');
  if (countEl) countEl.textContent = `${visible} place${visible !== 1 ? 's' : ''}`;
}

/* ============================================================
   PAGE: PLACE DETAILS
   ============================================================ */

function initPlacePage() {
  const section = document.getElementById('place-details');
  if (!section) return;

  const placeId = getQueryParam('id');
  if (!placeId) {
    section.innerHTML = '<p>No place ID in URL.</p>';
    return;
  }

  const token = getToken();
  fetchPlaceDetails(token, placeId);

  // Wire up "Write a review" CTA
  const link = document.getElementById('add-review-link');
  if (link) {
    link.href = `add_review.html?id=${encodeURIComponent(placeId)}`;
  }
}

async function fetchPlaceDetails(token, id) {
  try {
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_BASE}/places/${id}`, { headers });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const place = await response.json();
    displayPlace(place);
    displayReviews(place.reviews || []);

    // Show CTA only if logged in
    const cta = document.getElementById('add-review-cta');
    if (cta && token) cta.style.display = 'block';
  } catch (error) {
    console.error('fetchPlaceDetails:', error);
    document.getElementById('place-details').innerHTML = `
      <p>Could not load place details. <a href="index.html">← Back to places</a></p>`;
  }
}

function displayPlace(place) {
  const container = document.getElementById('place-details');
  const breadcrumb = document.getElementById('breadcrumb-name');

  if (breadcrumb) breadcrumb.textContent = place.name;

  const amenities = (place.amenities || [])
    .map(a => amenityTag(a))
    .join('');
  const placeImage = getPlaceImage(place);

  container.innerHTML = `
    <div class="place-hero">
      <div class="place-hero-media">
        <img src="${placeImage}" alt="${escapeHtml(place.name)}" loading="eager" />
        <div class="hero-badge">Featured stay</div>
      </div>
      <div class="place-hero-copy">
        <p class="hero-kicker">${escapeHtml(place.location || 'Unique stay')}</p>
        <h2>${escapeHtml(place.name)}</h2>
        <div class="detail-meta">
          <span class="chip price">€${place.price} / night</span>
          ${place.host ? `<span class="chip">🏠 Hosted by ${escapeHtml(place.host)}</span>` : ''}
          ${place.location ? `<span class="chip">📍 ${escapeHtml(place.location)}</span>` : ''}
        </div>
        <p class="place-description">${escapeHtml(place.description || '')}</p>
        ${amenities ? `<div class="amenities-list">${amenities}</div>` : ''}
      </div>
    </div>
  `;
}

function displayReviews(reviews) {
  const container = document.getElementById('reviews-list');
  if (!container) return;

  if (!reviews.length) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="icon">💬</div>
        <h3>No reviews yet</h3>
        <p>Be the first to share your experience.</p>
      </div>`;
    return;
  }

  container.innerHTML = reviews.map(r => `
    <div class="review-card">
      <div class="reviewer">
        <div class="reviewer-avatar">${(r.user || 'A')[0].toUpperCase()}</div>
        ${escapeHtml(r.user || 'Anonymous')}
        ${r.rating ? `<span style="margin-left:auto;color:#E8A020;">${'★'.repeat(r.rating)}</span>` : ''}
      </div>
      <p>${escapeHtml(r.text || '')}</p>
    </div>
  `).join('');
}

/* ============================================================
   PAGE: ADD REVIEW
   ============================================================ */

function initAddReviewPage() {
  const form = document.getElementById('review-form');
  if (!form) return;

  // Guard: must be logged in
  const token = checkAuth();

  const placeId = getQueryParam('id');
  if (!placeId) {
    showToast('No place specified.', 'error');
    return;
  }

  // Back link
  const placeLink = document.getElementById('breadcrumb-place-link');
  if (placeLink) placeLink.href = `place.html?id=${encodeURIComponent(placeId)}`;

  // Star rating interaction
  initStarRating();

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const text   = document.getElementById('review-text').value.trim();
    const rating = parseInt(document.getElementById('rating').value);
    const btn    = document.getElementById('submit-btn');

    if (!text) { showToast('Please write your review.', 'error'); return; }
    if (rating === 0) { showToast('Please select a star rating.', 'error'); return; }

    setButtonLoading(btn, true);
    await submitReview(token, placeId, text, rating);
    setButtonLoading(btn, false);
  });
}

function initStarRating() {
  const stars  = document.querySelectorAll('.star');
  const hidden = document.getElementById('rating');

  stars.forEach(star => {
    star.addEventListener('mouseenter', () => highlightStars(stars, star.dataset.value));
    star.addEventListener('mouseleave', () => highlightStars(stars, hidden.value));
    star.addEventListener('click', () => {
      hidden.value = star.dataset.value;
      highlightStars(stars, star.dataset.value);
    });
  });
}

function highlightStars(stars, value) {
  stars.forEach(s => {
    s.classList.toggle('active', parseInt(s.dataset.value) <= parseInt(value));
  });
}

async function submitReview(token, placeId, text, rating) {
  try {
    const response = await fetch(`${API_BASE}/reviews`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ place_id: placeId, text, rating })
    });

    if (response.ok) {
      showToast('Review submitted! Thank you.', 'success');
      setTimeout(() => {
        window.location.href = `place.html?id=${encodeURIComponent(placeId)}`;
      }, 1200);
    } else {
      const err = await response.json().catch(() => ({}));
      showToast(err.message || 'Failed to submit review.', 'error');
    }
  } catch (error) {
    showToast('Cannot reach the server.', 'error');
  }
}

const AMENITY_ICONS = {
  'WiFi':             'images/icon_wifi.png',
  'Bed':              'images/icon_bed.png',
  'Bath':             'images/icon_bath.png',
  'Shower':           'images/icon_bath.png',
  'Air conditioning': 'images/icon_air_conditioning.png',
  'Balcony':          'images/icon_balcony.png',
  'Dishwasher':       'images/icon_dishwasher.png',
  'Garden':           'images/icon_garden.png',
  'Heating':          'images/icon_heating.png',
  'Elevator':         'images/icon_elevator.png',
  'Kitchen':          'images/icon_kitchen.png',
  'Parking':          'images/icon_parking.png',
  'Pool':             'images/icon_pool.png',
  'BBQ':              'images/icon_bbq.png',
  'Shared kitchen':   'images/icon_shared_kitchen.png',
};

function amenityTag(name) {
  const icon = AMENITY_ICONS[name];
  const img  = icon
    ? `<img src="${icon}" alt="" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;opacity:0.7;">`
    : '';

  return `<span class="amenity-tag">${img}${escapeHtml(name)}</span>`;
}

function getPlaceImage(place) {
  if (place && place.image) {
    if (place.image.startsWith('/images/')) {
      return `${API_BASE}${place.image}`;
    }
    return place.image;
  }

  const title = escapeHtml((place && place.name) ? place.name : 'HBnB');
  const location = escapeHtml((place && place.location) ? place.location : 'Stay');
  const svg = `
    <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 900' role='img' aria-label='${title}'>
      <defs>
        <linearGradient id='bg' x1='0%' y1='0%' x2='100%' y2='100%'>
          <stop offset='0%' stop-color='#1F4D4F' />
          <stop offset='100%' stop-color='#E07A5F' />
        </linearGradient>
      </defs>
      <rect width='1200' height='900' fill='url(#bg)' />
      <circle cx='930' cy='180' r='190' fill='rgba(255,255,255,0.18)' />
      <circle cx='220' cy='720' r='220' fill='rgba(255,255,255,0.10)' />
      <rect x='70' y='110' rx='999' ry='999' width='220' height='58' fill='rgba(255,255,255,0.18)' />
      <text x='110' y='150' fill='white' font-family='Arial, sans-serif' font-size='28' font-weight='700'>HBnB stay</text>
      <text x='72' y='752' fill='white' font-family='Georgia, serif' font-size='88' font-weight='700'>${title}</text>
      <text x='74' y='818' fill='rgba(255,255,255,0.88)' font-family='Arial, sans-serif' font-size='34' letter-spacing='4'>${location}</text>
    </svg>
  `.trim();

  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}


function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ============================================================
   ROUTER — detect which page we're on and init it
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  syncAuthUI();

  const path = window.location.pathname;

  if (path.endsWith('login.html'))      initLoginPage();
  else if (path.endsWith('index.html') || path.endsWith('/') || path === '') initIndexPage();
  else if (path.endsWith('place.html')) initPlacePage();
  else if (path.endsWith('add_review.html')) initAddReviewPage();
});
