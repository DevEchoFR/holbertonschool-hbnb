/* ============================================================
   scripts.js — HBnB Frontend Logic
   ============================================================ */

// Detect the correct backend URL regardless of environment:
//
//  Local (no forwarding)  → frontend :5001, backend :5000
//  VS Code port forwarding → frontend forwarded to :5002, backend forwarded to :5001
//  GitHub Codespaces URL  → frontend xxx-5001.app.github.dev,
//                            backend  xxx-5000.app.github.dev
//
// Rule: backend port = frontend port - 1 (gap is always 1).
const API_BASE = (() => {
  const { hostname, port, protocol } = window.location;

  // Codespace / Remote tunnel public URL (*.app.github.dev, *.github.dev, etc.)
  if (hostname.includes('.github.dev') || hostname.includes('.githubpreview.dev')) {
    return window.location.origin.replace(/-(\d+)(\.app\.github\.dev|\.githubpreview\.dev)/, (_, p, suffix) => `-${parseInt(p, 10) - 1}${suffix}`);
  }

  // localhost / 127.0.0.1 with VS Code port forwarding (port > 5000)
  const frontendPort = parseInt(port || '80', 10);
  if (frontendPort > 5000) {
    return `${protocol}//${hostname}:${frontendPort - 1}`;
  }

  // Plain local dev (frontend served directly from disk or port 5001 without shift)
  return 'http://localhost:5000';
})();
const API_V1_BASE = `${API_BASE}/api/v1`;

function apiV1(path) {
  return `${API_V1_BASE}${path}`;
}

/* ─── UTILITIES ─── */

function getCookie(name) {
  const cookieArray = document.cookie.split('; ');
  for (const cookie of cookieArray) {
    const [cookieName, ...cookieValueParts] = cookie.split('=');
    if (cookieName === name) {
      return cookieValueParts.join('='); // Handle values that contain '='
    }
  }
  return null;
}

function setCookie(name, value, days = 7) {
  const expires = new Date(Date.now() + days * 86400000).toUTCString();
  document.cookie = `${name}=${value}; expires=${expires}; path=/; SameSite=Lax`;
}

function deleteCookie(name) {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/`;
}

function getQueryParam(key) {
  const params = new URLSearchParams(window.location.search);
  return params.get(key) || '';
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
  const raw = getCookie('token');
  if (!raw) return null;
  
  // Handle both URL-encoded and plain tokens
  try {
    // Try to decode if it looks URL-encoded (contains %xx patterns)
    if (raw.includes('%')) {
      return decodeURIComponent(raw);
    }
    return raw;
  } catch (e) {
    // If decoding fails, return as-is
    return raw;
  }
}

function saveCurrentUser(user) {
  if (!user) return;
  localStorage.setItem('currentUser', JSON.stringify(user));
}

function getCurrentUser() {
  try {
    const raw = localStorage.getItem('currentUser');
    return raw ? JSON.parse(raw) : null;
  } catch (error) {
    return null;
  }
}

function clearAuthState() {
  deleteCookie('token');
  localStorage.removeItem('currentUser');
}

async function fetchCurrentUser(token) {
  const response = await fetch(apiV1('/auth/me'), {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!response.ok) {
    throw new Error('Could not load current user.');
  }
  return response.json();
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
  const user = getCurrentUser();
  const btn = document.getElementById('header-login-btn');
  const navLink = document.getElementById('nav-login-link');
  const adminLink = document.getElementById('admin-link');

  if (adminLink) {
    if (token && user && user.is_admin) {
      adminLink.style.display = 'inline-flex';
    } else {
      adminLink.style.display = 'none';
    }
  }

  if (token && btn) {
    btn.textContent = 'Logout';
    btn.href = '#';
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      clearAuthState();
      window.location.href = 'login.html';
    });
  }
  if (token && navLink) {
    navLink.textContent = 'Logout';
    navLink.href = '#';
    navLink.addEventListener('click', (e) => {
      e.preventDefault();
      clearAuthState();
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
    const response = await fetch(apiV1('/auth/login'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (response.ok) {
      const data = await response.json();
      setCookie('token', data.access_token);
      if (data.user) {
        saveCurrentUser(data.user);
      } else {
        const profile = await fetchCurrentUser(data.access_token);
        saveCurrentUser(profile);
      }
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
   PAGE: SIGNUP
   ============================================================ */

function initSignupPage() {
  const form = document.getElementById('signup-form');
  if (!form) return;

  // Redirect if already logged in
  if (getToken()) {
    window.location.href = 'index.html';
    return;
  }

  form.addEventListener('submit', handleSignup);
}

async function handleSignup(e) {
  e.preventDefault();

  const name = document.getElementById('name').value.trim();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const passwordConfirm = document.getElementById('password-confirm').value;
  const btn = document.getElementById('signup-btn');

  if (!name || !email || !password || !passwordConfirm) {
    showToast('Please fill in all fields.', 'error');
    return;
  }

  if (password !== passwordConfirm) {
    showToast('Passwords do not match.', 'error');
    return;
  }

  const [firstName, ...restNames] = name.split(/\s+/).filter(Boolean);
  const lastName = restNames.join(' ') || 'User';

  setButtonLoading(btn, true);

  try {
    const payload = {
      first_name: firstName || 'User',
      last_name: lastName,
      email,
      password
    };

    const response = await fetch(apiV1('/users/'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (response.ok || response.status === 201) {
      const loginResponse = await fetch(apiV1('/auth/login'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!loginResponse.ok) {
        throw new Error('Account created but auto-login failed.');
      }

      const loginData = await loginResponse.json();
      setCookie('token', loginData.access_token);
      if (loginData.user) {
        saveCurrentUser(loginData.user);
      } else {
        const profile = await fetchCurrentUser(loginData.access_token);
        saveCurrentUser(profile);
      }

      showToast('Account created! Redirecting…', 'success');
      setTimeout(() => { window.location.href = 'index.html'; }, 800);
    } else {
      const err = await response.json().catch(() => ({}));
      showToast(err.message || 'Signup failed. Please try again.', 'error');
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

  const searchForm = document.getElementById('home-search-form');
  const searchInput = document.getElementById('home-search');

  if (searchForm) {
    searchForm.addEventListener('submit', (event) => {
      event.preventDefault();
      applyHomepageFilters();
      document.getElementById('featured-stays')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  if (searchInput) {
    searchInput.addEventListener('input', applyHomepageFilters);
  }
}

async function fetchPlaces(token) {
  try {
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(apiV1('/places/'), { headers });

    if (response.status === 401) {
      // Show places anyway if API allows, or redirect
      showToast('Sign in to see all places.', '');
    }

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const apiPlaces = await response.json();
    allPlaces = dedupePlaces(apiPlaces.map(normalizePlace));
    applyHomepageFilters();
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

function applyHomepageFilters() {
  const maxPrice = document.getElementById('price-filter')?.value || 'All';
  const query = document.getElementById('home-search')?.value.trim().toLowerCase() || '';

  const filtered = allPlaces.filter((place) => {
    const price = Number(place.price || 0);
    const priceMatches = maxPrice === 'All' || price <= Number(maxPrice);

    const searchableText = [
      place.name,
      place.description,
      place.location,
      place.host,
      ...(place.amenities || [])
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();

    const queryMatches = !query || searchableText.includes(query);
    return priceMatches && queryMatches;
  });

  displayPlaces(filtered);
}

function displayPlaces(places) {
  const container = document.getElementById('places-list');
  const countEl   = document.getElementById('result-count');
  const usedImages = new Set();

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
    const placeImage = getPlaceImage(place, usedImages);
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
  applyHomepageFilters();
}

function normalizePlace(rawPlace) {
  const amenities = Array.isArray(rawPlace.amenities)
    ? rawPlace.amenities.map((item) => {
      if (typeof item === 'string') return item;
      return item && item.name ? item.name : '';
    }).filter(Boolean)
    : [];

  const host = rawPlace.host
    || (rawPlace.owner
      ? `${rawPlace.owner.first_name || ''} ${rawPlace.owner.last_name || ''}`.trim()
      : 'HBnB');

  const location = rawPlace.location
    || ((rawPlace.latitude !== undefined && rawPlace.longitude !== undefined)
      ? `${Number(rawPlace.latitude).toFixed(4)}, ${Number(rawPlace.longitude).toFixed(4)}`
      : 'Location unavailable');

  const reviews = Array.isArray(rawPlace.reviews)
    ? rawPlace.reviews.map((review) => ({
      ...review,
      user: review.user || review.author || 'Guest'
    }))
    : [];

  return {
    ...rawPlace,
    name: rawPlace.name || rawPlace.title || 'Untitled stay',
    title: rawPlace.title || rawPlace.name || 'Untitled stay',
    description: rawPlace.description || '',
    price: Number(rawPlace.price || 0),
    host,
    location,
    amenities,
    reviews
  };
}

function dedupePlaces(places) {
  const seen = new Set();

  return places.filter((place) => {
    const key = [
      place.name || place.title || '',
      place.location || '',
      place.host || '',
      place.price || '',
    ]
      .join('|')
      .toLowerCase();

    if (seen.has(key)) {
      return false;
    }

    seen.add(key);
    return true;
  });
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

    const response = await fetch(apiV1(`/places/${id}`), { headers });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const place = normalizePlace(await response.json());
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
    let currentUser = getCurrentUser();
    if (!currentUser) {
      currentUser = await fetchCurrentUser(token);
      saveCurrentUser(currentUser);
    }
    const response = await fetch(apiV1('/reviews/'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        place_id: placeId,
        text,
        rating,
        user_id: currentUser ? currentUser.id : ''
      })
    });

    if (response.ok) {
      showToast('Review submitted! Thank you.', 'success');
      setTimeout(() => {
        window.location.href = `place.html?id=${encodeURIComponent(placeId)}`;
      }, 1200);
    } else if (response.status === 401) {
      clearAuthState();
      showToast('Your session expired. Please login again.', 'error');
      setTimeout(() => {
        window.location.href = 'login.html';
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

const ROOM_IMAGES = [
  {
    keywords: ['budget room', 'latin quarter'],
    file: 'Budget Room in the Latin Quarter.jpg',
  },
  {
    keywords: ['hidden storage', 'storage', 'furniture ideas', 'minimalist'],
    file: 'Hidden Storage Furniture Ideas.jpg',
  },
  {
    keywords: ['cosy studio', 'cozy studio', 'montmartre'],
    file: 'Cosy Studio in Montmartre.jpg',
  },
  {
    keywords: ['charming provence farmhouse', 'provence farmhouse', 'farmhouse'],
    file: 'Charming Provence Farmhouse.jpg',
  },
  {
    keywords: ['modern loft', 'eiffel tower', 'loft'],
    file: 'Modern Loft near the Eiffel Tower.jpg',
  },
  {
    keywords: ['warm minimalist tropical loft', 'tropical loft', 'luxury natural interior design inspiration', 'minimalist'],
    file: 'Warm Minimalist Tropical Loft – Luxury Natural Interior Design Inspiration.jpg',
  },
  {
    keywords: ['download', 'neutral room', 'guest room', 'placeholder'],
    file: 'download.jpg',
  },
];

function roomImageUrl(fileName) {
  return `images/${encodeURI(fileName)}`;
}

function hashRoomSeed(seedText) {
  const normalized = String(seedText || '').toLowerCase();
  let hash = 0;
  for (let index = 0; index < normalized.length; index += 1) {
    hash = (hash * 31 + normalized.charCodeAt(index)) >>> 0;
  }
  return hash;
}

function fallbackRoomImage(seedText, usedImages = new Set(), preferredFile = null) {
  const hash = hashRoomSeed(seedText);
  const startIndex = hash % ROOM_IMAGES.length;
  const candidateFiles = [];

  if (preferredFile) {
    candidateFiles.push(preferredFile);
  }

  for (let offset = 0; offset < ROOM_IMAGES.length; offset += 1) {
    candidateFiles.push(ROOM_IMAGES[(startIndex + offset) % ROOM_IMAGES.length].file);
  }

  for (const fileName of candidateFiles) {
    if (!usedImages.has(fileName)) {
      usedImages.add(fileName);
      return roomImageUrl(fileName);
    }
  }

  const fallbackFile = preferredFile || ROOM_IMAGES[startIndex].file;
  return roomImageUrl(fallbackFile);
}

function getPlaceImage(place, usedImages = null) {
  if (place && place.image) {
    if (place.image.startsWith('/images/')) {
      return `${API_BASE}${place.image}`;
    }
    return place.image;
  }

  const lookupText = [
    place && place.name,
    place && place.title,
    place && place.location,
    place && place.description,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();

  const matchedRoom = ROOM_IMAGES.find((roomImage) =>
    roomImage.keywords.some((keyword) => lookupText.includes(keyword))
  );

  if (usedImages) {
    return fallbackRoomImage(
      lookupText || (place && place.id) || 'hbnb',
      usedImages,
      matchedRoom ? matchedRoom.file : null,
    );
  }

  if (matchedRoom) {
    return roomImageUrl(matchedRoom.file);
  }

  return fallbackRoomImage(lookupText || (place && place.id) || 'hbnb');
}


function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ============================================================
   PAGE: CREATE / EDIT PLACE
   ============================================================ */

/* ── Amenity checklist helpers ─────────────────────────────────────────── */

async function loadAmenityChecklist(selectedIds = []) {
  const container = document.getElementById('amenities-checklist');
  if (!container) return;

  try {
    const res = await fetch(apiV1('/amenities/'));
    if (!res.ok) throw new Error('Failed to load amenities');
    const amenities = await res.json();

    if (!amenities.length) {
      container.innerHTML = '<span class="amenities-loading">No amenities available.</span>';
      return;
    }

    const selectedSet = new Set(selectedIds);
    container.innerHTML = amenities.map((a) => `
      <label class="amenity-checkbox">
        <input type="checkbox" name="amenity" value="${escapeHtml(a.id)}"
          ${selectedSet.has(a.id) ? 'checked' : ''} />
        ${escapeHtml(a.name)}
      </label>
    `).join('');
  } catch {
    container.innerHTML = '<span class="amenities-loading">Could not load amenities.</span>';
  }
}

function getCheckedAmenityIds() {
  return Array.from(
    document.querySelectorAll('#amenities-checklist input[name="amenity"]:checked')
  ).map((cb) => cb.value);
}

async function fetchPlaceForEditing(placeId, token) {
  const response = await fetch(apiV1(`/places/${placeId}`), {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!response.ok) {
    throw new Error('Unable to load place for editing.');
  }
  return response.json();
}

function fillPlaceForm(place) {
  const normalized = normalizePlace(place);
  document.getElementById('place-name').value = normalized.name || '';
  document.getElementById('place-description').value = place.description || '';
  document.getElementById('place-price').value = place.price || '';
  document.getElementById('place-latitude').value = place.latitude ?? '';
  document.getElementById('place-longitude').value = place.longitude ?? '';
  // Amenity checkboxes are pre-checked inside loadAmenityChecklist()
}

function collectPlaceFormData(includeOwnerId = true) {
  const currentUser = getCurrentUser();
  const payload = {
    title: document.getElementById('place-name').value.trim(),
    description: document.getElementById('place-description').value.trim(),
    price: Number(document.getElementById('place-price').value),
    latitude: Number(document.getElementById('place-latitude').value),
    longitude: Number(document.getElementById('place-longitude').value),
    amenity_ids: getCheckedAmenityIds(),
  };

  if (includeOwnerId) {
    payload.owner_id = currentUser ? currentUser.id : '';
  }

  return payload;
}

function validatePlacePayload(payload, options = {}) {
  const requireOwnerId = options.requireOwnerId !== false;
  if (!payload.title) {
    return 'Place name is required.';
  }
  if (!payload.price || Number.isNaN(payload.price) || payload.price <= 0) {
    return 'Price must be greater than zero.';
  }
  if (Number.isNaN(payload.latitude) || payload.latitude === '' || payload.latitude === null) {
    return 'Latitude is required.';
  }
  if (Number.isNaN(payload.longitude) || payload.longitude === '' || payload.longitude === null) {
    return 'Longitude is required.';
  }
  if (requireOwnerId && !payload.owner_id) {
    return 'You must be logged in to create a place.';
  }
  return '';
}

/* Shared form logic used by both create_place.html and edit_place.html */
async function initPlaceForm(placeId) {
  const form = document.getElementById('place-form');
  if (!form) return;

  const token = checkAuth();
  if (!token) return;

  // Ensure we have the authenticated user's profile
  let authenticatedUser = getCurrentUser();
  if (!authenticatedUser || !authenticatedUser.id) {
    try {
      authenticatedUser = await fetchCurrentUser(token);
      saveCurrentUser(authenticatedUser);
    } catch (error) {
      showToast('Please login again to continue.', 'error');
      clearAuthState();
      setTimeout(() => { window.location.href = 'login.html'; }, 800);
      return;
    }
  }

  form.dataset.authenticatedUserId = authenticatedUser.id;

  const submitBtn = document.getElementById('place-submit-btn');
  const isEdit = Boolean(placeId);

  if (isEdit) {
    try {
      const place = await fetchPlaceForEditing(placeId, token);
      const existingIds = Array.isArray(place.amenity_ids)
        ? place.amenity_ids
        : (place.amenities || []).map((a) => a.id || a).filter(Boolean);
      await loadAmenityChecklist(existingIds);
      fillPlaceForm(place);
    } catch (error) {
      showToast('Could not load place details.', 'error');
      await loadAmenityChecklist();
    }
  } else {
    await loadAmenityChecklist();
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const payload = collectPlaceFormData(false);

    if (!isEdit) {
      const authenticatedUserId = form.dataset.authenticatedUserId;
      if (!authenticatedUserId) {
        showToast('Authentication error: Please login again.', 'error');
        return;
      }
      payload.owner_id = authenticatedUserId;
    }

    const validationError = validatePlacePayload(payload, { requireOwnerId: !isEdit });
    if (validationError) {
      showToast(validationError, 'error');
      return;
    }

    setButtonLoading(submitBtn, true);
    try {
      const endpoint = isEdit ? apiV1(`/places/${placeId}`) : apiV1('/places/');
      const method   = isEdit ? 'PUT' : 'POST';

      const response = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const place = await response.json();
        showToast(isEdit ? 'Place updated successfully.' : 'Place created successfully.', 'success');
        setTimeout(() => {
          window.location.href = `place.html?id=${encodeURIComponent(place.id)}`;
        }, 900);
      } else {
        const err = await response.json().catch(() => ({}));
        showToast(err.message || 'Failed to save place.', 'error');
      }
    } catch (error) {
      showToast('Cannot reach the server.', 'error');
    } finally {
      setButtonLoading(submitBtn, false);
    }
  });
}

function initCreatePlacePage() {
  if (!document.getElementById('place-form')) return;
  initPlaceForm(null);
}

function initEditPlacePage() {
  if (!document.getElementById('place-form')) return;
  const raw = getQueryParam('id') || getQueryParam('place_id');
  const placeId = (raw && raw !== 'undefined' && raw !== 'null') ? raw.trim() : '';
  if (!placeId) {
    showToast('No place ID found in URL.', 'error');
    setTimeout(() => { window.location.href = 'admin.html'; }, 1200);
    return;
  }
  initPlaceForm(placeId);
}

/* Keep old name as alias so existing bookmarks to create_edit_place.html still work */
function initCreateEditPlacePage() {
  if (!document.getElementById('place-form')) return;
  const raw = getQueryParam('id') || getQueryParam('place_id');
  const placeId = (raw && raw !== 'undefined' && raw !== 'null') ? raw.trim() : '';
  initPlaceForm(placeId || null);
}

/* ============================================================
   PAGE: ADMIN
   ============================================================ */

function renderAdminOverview(data) {
  const stats = data.stats || {};
  document.getElementById('admin-users-count').textContent = stats.users || 0;
  document.getElementById('admin-places-count').textContent = stats.places || 0;
  document.getElementById('admin-reviews-count').textContent = stats.reviews || 0;

  const currentUser = getCurrentUser();
  const usersList   = document.getElementById('admin-users-list');
  const placesList  = document.getElementById('admin-places-list');
  const reviewsList = document.getElementById('admin-reviews-list');

  // ── Users ──────────────────────────────────────────────────────────────────
  usersList.innerHTML = (data.users || []).map((user) => {
    const fullName = escapeHtml(
      `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'User'
    );
    const isSelf    = currentUser && currentUser.id === user.id;
    const roleLabel = user.is_admin ? ' <strong>(admin)</strong>' : '';
    const roleBtn   = isSelf ? '' :
      `<button class="admin-role-btn" data-user-id="${escapeHtml(user.id)}" data-is-admin="${user.is_admin}">
        ${user.is_admin ? 'Revoke admin' : 'Make admin'}
      </button>`;
    const editBtn   =
      `<button class="admin-edit-btn" data-user-id="${escapeHtml(user.id)}"
         data-first-name="${escapeHtml(user.first_name || '')}"
         data-last-name="${escapeHtml(user.last_name || '')}"
         data-email="${escapeHtml(user.email || '')}">Edit</button>`;
    const deleteBtn = isSelf ? '' :
      `<button class="admin-delete-btn" data-user-id="${escapeHtml(user.id)}"
         data-user-name="${escapeHtml(fullName)}">Delete</button>`;

    return `<li>
      <span class="admin-item-label">${fullName} <em>${escapeHtml(user.email || '')}</em>${roleLabel}</span>
      <div class="admin-actions">${editBtn}${roleBtn}${deleteBtn}</div>
    </li>`;
  }).join('');

  // Wire up user action buttons
  usersList.querySelectorAll('.admin-role-btn').forEach((btn) => {
    btn.addEventListener('click', () => adminToggleRole(btn));
  });
  usersList.querySelectorAll('.admin-edit-btn').forEach((btn) => {
    btn.addEventListener('click', () => adminEditUser(btn));
  });
  usersList.querySelectorAll('[data-user-id].admin-delete-btn').forEach((btn) => {
    btn.addEventListener('click', () => adminDeleteUser(btn));
  });

  // ── Places ─────────────────────────────────────────────────────────────────
  placesList.innerHTML = (data.places || []).map((place) => {
    const placeId = place.id || '';
    if (!placeId) {
      return `<li><span>${escapeHtml(place.name)} — €${place.price}</span></li>`;
    }
    const editUrl = `edit_place.html?id=${encodeURIComponent(placeId)}`;
    return `<li>
      <span>${escapeHtml(place.name)} — €${place.price}</span>
      <div class="admin-actions">
        <a href="${editUrl}">Modify</a>
        <button class="admin-delete-btn" data-place-id="${escapeHtml(placeId)}" data-place-name="${escapeHtml(place.name)}">Delete</button>
      </div>
    </li>`;
  }).join('');

  // Wire up place delete buttons
  placesList.querySelectorAll('.admin-delete-btn').forEach((btn) => {
    btn.addEventListener('click', () => adminDeletePlace(btn));
  });

  // ── Reviews ────────────────────────────────────────────────────────────────
  // Build a place-id → title lookup so reviews show place names, not UUIDs
  const placeMap = {};
  (data.places || []).forEach((p) => { if (p.id) placeMap[p.id] = p.name || p.title || p.id; });

  reviewsList.innerHTML = (data.reviews || []).map((review) => {
    const placeName = placeMap[review.place_id] || review.place_id || 'Unknown place';
    return `<li>
      <span>${escapeHtml(review.user || 'Anonymous')} on <em>${escapeHtml(placeName)}</em>: ${escapeHtml(review.text || '')}</span>
    </li>`;
  }).join('');
}

async function adminToggleRole(btn) {
  const token    = getToken();
  const userId   = btn.dataset.userId;
  const makeAdmin = btn.dataset.isAdmin === 'true' ? false : true;

  btn.disabled = true;
  btn.textContent = 'Saving…';

  try {
    const res = await fetch(apiV1(`/admin/users/${userId}/role`), {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ is_admin: makeAdmin })
    });

    if (res.ok) {
      showToast(makeAdmin ? 'Admin role granted.' : 'Admin role revoked.', 'success');
      // Refresh the admin panel to reflect the change
      initAdminPage();
    } else {
      const err = await res.json().catch(() => ({}));
      showToast(err.message || 'Failed to update role.', 'error');
      btn.disabled = false;
      btn.textContent = makeAdmin ? 'Make admin' : 'Revoke admin';
    }
  } catch {
    showToast('Cannot reach the server.', 'error');
    btn.disabled = false;
    btn.textContent = makeAdmin ? 'Make admin' : 'Revoke admin';
  }
}

async function adminDeletePlace(btn) {
  const token     = getToken();
  const placeId   = btn.dataset.placeId;
  const placeName = btn.dataset.placeName || 'this place';

  if (!confirm(`Delete "${placeName}"? This cannot be undone.`)) return;

  btn.disabled = true;
  btn.textContent = 'Deleting…';

  try {
    const res = await fetch(apiV1(`/places/${placeId}`), {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (res.ok) {
      showToast('Place deleted.', 'success');
      initAdminPage();
    } else {
      const err = await res.json().catch(() => ({}));
      showToast(err.message || 'Failed to delete place.', 'error');
      btn.disabled = false;
      btn.textContent = 'Delete';
    }
  } catch {
    showToast('Cannot reach the server.', 'error');
    btn.disabled = false;
    btn.textContent = 'Delete';
  }
}

async function adminEditUser(btn) {
  const userId    = btn.dataset.userId;
  const firstName = btn.dataset.firstName || '';
  const lastName  = btn.dataset.lastName  || '';
  const email     = btn.dataset.email     || '';
  const token     = getToken();

  // Build a simple inline modal prompt
  const newFirst = window.prompt('First name:', firstName);
  if (newFirst === null) return; // cancelled
  const newLast  = window.prompt('Last name:',  lastName);
  if (newLast  === null) return;
  const newEmail = window.prompt('Email:',      email);
  if (newEmail === null) return;

  const payload = {};
  if (newFirst.trim() !== firstName) payload.first_name = newFirst.trim();
  if (newLast.trim()  !== lastName)  payload.last_name  = newLast.trim();
  if (newEmail.trim() !== email)     payload.email      = newEmail.trim();

  if (!Object.keys(payload).length) {
    showToast('No changes made.', '');
    return;
  }

  btn.disabled = true;
  try {
    const res = await fetch(apiV1(`/admin/users/${userId}`), {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      showToast('User updated.', 'success');
      initAdminPage();
    } else {
      const err = await res.json().catch(() => ({}));
      showToast(err.message || 'Failed to update user.', 'error');
      btn.disabled = false;
    }
  } catch {
    showToast('Cannot reach the server.', 'error');
    btn.disabled = false;
  }
}

async function adminDeleteUser(btn) {
  const userId   = btn.dataset.userId;
  const userName = btn.dataset.userName || 'this user';
  const token    = getToken();

  if (!confirm(`Delete user "${userName}"? This cannot be undone.`)) return;

  btn.disabled = true;
  btn.textContent = 'Deleting…';

  try {
    const res = await fetch(apiV1(`/admin/users/${userId}`), {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) {
      showToast('User deleted.', 'success');
      initAdminPage();
    } else {
      const err = await res.json().catch(() => ({}));
      showToast(err.message || 'Failed to delete user.', 'error');
      btn.disabled = false;
      btn.textContent = 'Delete';
    }
  } catch {
    showToast('Cannot reach the server.', 'error');
    btn.disabled = false;
    btn.textContent = 'Delete';
  }
}

async function initAdminPage() {
  const panel = document.getElementById('admin-panel');
  if (!panel) return;

  const token = checkAuth();
  let user = getCurrentUser();
  if (!user || !user.id) {
    try {
      user = await fetchCurrentUser(token);
      saveCurrentUser(user);
    } catch (error) {
      // Token expired or invalid
      clearAuthState();
      showToast('Your session has expired. Please login again.', 'error');
      setTimeout(() => { window.location.href = 'login.html'; }, 1200);
      return;
    }
  }
  if (!user || !user.is_admin) {
    panel.innerHTML = '<p class="empty-state">Admin access required.</p>';
    return;
  }

  try {
    const [usersRes, placesRes] = await Promise.all([
      fetch(apiV1('/admin/users'), {
        headers: { 'Authorization': `Bearer ${token}` }
      }),
      fetch(apiV1('/places/'), {
        headers: { 'Authorization': `Bearer ${token}` }
      })
    ]);

    // Token expired or revoked — kick to login
    if (usersRes.status === 401 || placesRes.status === 401) {
      clearAuthState();
      showToast('Your session has expired. Please login again.', 'error');
      setTimeout(() => { window.location.href = 'login.html'; }, 1200);
      return;
    }

    if (usersRes.status === 403 || placesRes.status === 403) {
      panel.innerHTML = '<p class="empty-state">Admin access required.</p>';
      return;
    }

    if (!usersRes.ok || !placesRes.ok) {
      throw new Error('Failed to load admin data.');
    }

    const users = await usersRes.json();
    const places = dedupePlaces((await placesRes.json()).map(normalizePlace));
    const reviews = places.flatMap((place) => place.reviews || []);

    renderAdminOverview({
      stats: {
        users: users.length,
        places: places.length,
        reviews: reviews.length
      },
      users,
      places,
      reviews
    });
  } catch (error) {
    panel.innerHTML = '<p class="empty-state">Could not load admin data.</p>';
  }
}

/* ============================================================
   ROUTER — detect which page we're on and init it
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  syncAuthUI();

  const path = window.location.pathname;

  if (path.endsWith('signup.html'))              initSignupPage();
  else if (path.endsWith('login.html'))           initLoginPage();
  else if (path.endsWith('index.html') || path.endsWith('/') || path === '') initIndexPage();
  else if (path.endsWith('place.html'))           initPlacePage();
  else if (path.endsWith('add_review.html'))      initAddReviewPage();
  else if (path.endsWith('create_place.html'))    initCreatePlacePage();
  else if (path.endsWith('edit_place.html'))      initEditPlacePage();
  else if (path.endsWith('create_edit_place.html')) initCreateEditPlacePage();
  else if (path.endsWith('admin.html'))           initAdminPage();
});
