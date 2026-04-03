/* ============================================================
   scripts.js — HBnB Frontend Logic
   ============================================================ */

const API_BASE = 'http://localhost:5000';
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
    const response = await fetch(apiV1('/users/'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        first_name: firstName || 'User',
        last_name: lastName,
        email,
        password
      })
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

function parseAmenitiesInput(value) {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
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
  
  // Amenities can come as either amenity_ids array or as amenities object array
  let amenityIds = [];
  if (place.amenity_ids && Array.isArray(place.amenity_ids)) {
    amenityIds = place.amenity_ids;
  } else if (place.amenities && Array.isArray(place.amenities)) {
    amenityIds = place.amenities.map(a => a.id || a);
  }
  document.getElementById('place-amenities').value = amenityIds.join(', ');
}

function collectPlaceFormData(includeOwnerId = true) {
  const currentUser = getCurrentUser();
  const payload = {
    title: document.getElementById('place-name').value.trim(),
    description: document.getElementById('place-description').value.trim(),
    price: Number(document.getElementById('place-price').value),
    latitude: Number(document.getElementById('place-latitude').value),
    longitude: Number(document.getElementById('place-longitude').value),
    amenity_ids: parseAmenitiesInput(document.getElementById('place-amenities').value)
  };

  if (includeOwnerId) {
    payload.owner_id = currentUser ? currentUser.id : '';
  }

  return payload;
}

function validatePlacePayload(payload, options = {}) {
  const requireOwnerId = options.requireOwnerId !== false;
  if (!payload.title || !payload.description) {
    return 'Name and description are required.';
  }
  if (!payload.price || Number.isNaN(payload.price) || payload.price <= 0) {
    return 'Price must be greater than zero.';
  }
  if (Number.isNaN(payload.latitude) || Number.isNaN(payload.longitude)) {
    return 'Latitude and longitude are required.';
  }
  if (requireOwnerId && !payload.owner_id) {
    return 'You must be logged in to create a place.';
  }
  return '';
}

async function initCreateEditPlacePage() {
  const form = document.getElementById('place-form');
  if (!form) {
    console.error('Place form element not found!');
    return;
  }

  // Check direct URL parameters
  console.log('=== INIT CREATE/EDIT PAGE ===');
  console.log('Full URL:', window.location.href);
  console.log('Pathname:', window.location.pathname);
  console.log('Search (query string):', window.location.search);
  
  // Ensure we have authentication before proceeding
  const token = checkAuth();
  if (!token) {
    console.error('No token found, checkAuth should have redirected but did not');
    return;
  }
  
  console.log('Token found, proceeding with page initialization');
  
  // Get the authenticated user - this is crucial for place creation
  let authenticatedUser = getCurrentUser();
  if (!authenticatedUser || !authenticatedUser.id) {
    console.log('Fetching authenticated user from API...');
    try {
      authenticatedUser = await fetchCurrentUser(token);
      console.log('Fetched authenticatedUser:', authenticatedUser);
      saveCurrentUser(authenticatedUser);
    } catch (error) {
      console.error('Failed to fetch authenticated user:', error);
      showToast('Please login again to continue.', 'error');
      clearAuthState();
      setTimeout(() => { window.location.href = 'login.html'; }, 800);
      return;
    }
  } else {
    console.log('authenticatedUser already in localStorage:', authenticatedUser);
  }
  
  // Store the authenticated user ID on the form for later use
  form.dataset.authenticatedUserId = authenticatedUser.id;
  console.log('Stored authenticatedUserId on form:', authenticatedUser.id);
  
  // Try multiple approaches to extract the place ID
  let placeId = '';
  
  // Approach 1: Direct parsing of window.location.search
  if (window.location.search) {
    const exactMatch = window.location.search.match(/[?&]id=([^&]+)/);
    if (exactMatch) {
      placeId = decodeURIComponent(exactMatch[1]);
      console.log('Found id via regex from search string:', placeId);
    }
  }
  
  // Approach 2: URLSearchParams (more robust)
  if (!placeId && window.location.search) {
    const urlParams = new URLSearchParams(window.location.search);
    const idFromUrl = urlParams.get('id');
    if (idFromUrl) {
      placeId = idFromUrl;
      console.log('Found id via URLSearchParams:', placeId);
    }
  }
  
  // Approach 3: Fallback to getQueryParam
  if (!placeId) {
    const fallback = getQueryParam('id') || getQueryParam('place_id');
    if (fallback) {
      placeId = fallback;
      console.log('Found id via getQueryParam:', placeId);
    }
  }
  
  // Trim and validate
  if (placeId) {
    placeId = placeId.trim();
  }
  
  if (placeId === 'undefined' || placeId === 'null' || placeId === '') {
    placeId = '';
  }
    
  // Debug logging
  console.log('Final extracted placeId:', placeId);
  console.log('Is edit mode?', Boolean(placeId));
  
  const heading = document.getElementById('place-form-title');
  const breadcrumb = document.getElementById('place-form-breadcrumb');
  const submitBtn = document.getElementById('place-submit-btn');

  if (placeId) {
    console.log('=== EDIT MODE ===', 'Loading place:', placeId);
    if (heading) heading.textContent = 'Edit place';
    if (breadcrumb) breadcrumb.textContent = 'Edit place';
    if (submitBtn) submitBtn.textContent = 'Save changes';
    try {
      const place = await fetchPlaceForEditing(placeId, token);
      console.log('Fetched place data:', place);
      fillPlaceForm(place);
    } catch (error) {
      console.error('Error loading place for editing:', error);
      showToast('Could not load place details.', 'error');
    }
  } else {
    console.log('=== CREATE MODE === No placeId provided');
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const isEdit = Boolean(placeId);
    console.log('Form submitted. Is edit mode?', isEdit);
    
    // Collect form data
    const payload = collectPlaceFormData(false); // Don't include owner_id from here
    
    // For CREATE mode, ALWAYS set owner_id from authenticated user
    if (!isEdit) {
      const authenticatedUserId = form.dataset.authenticatedUserId;
      if (!authenticatedUserId) {
        console.error('No authenticated user ID available!');
        showToast('Authentication error: Please login again.', 'error');
        return;
      }
      payload.owner_id = authenticatedUserId;
      console.log('CREATE mode: Set owner_id to', authenticatedUserId);
    }
    
    // Validate the payload
    const validationError = validatePlacePayload(payload, { requireOwnerId: !isEdit });
    if (validationError) {
      console.log('Validation failed:', validationError);
      showToast(validationError, 'error');
      return;
    }
    
    console.log('Validation passed. Payload:', payload);

    setButtonLoading(submitBtn, true);
    try {
      const endpoint = placeId ? apiV1(`/places/${placeId}`) : apiV1('/places/');
      const method = placeId ? 'PUT' : 'POST';
      
      console.log(`Sending ${method} request to ${endpoint}`);

      const response = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      console.log(`Response status: ${response.status}`);

      if (response.ok) {
        const place = await response.json();
        showToast(placeId ? 'Place updated successfully.' : 'Place created successfully.', 'success');
        console.log('Success! Redirecting to place details...');
        setTimeout(() => {
          window.location.href = `place.html?id=${encodeURIComponent(place.id)}`;
        }, 900);
      } else {
        const err = await response.json().catch(() => ({}));
        console.error('API returned error:', err);
        showToast(err.message || 'Failed to save place.', 'error');
      }
    } catch (error) {
      console.error('Network or submission error:', error);
      showToast('Cannot reach the server.', 'error');
    } finally {
      setButtonLoading(submitBtn, false);
    }
  });
}

/* ============================================================
   PAGE: ADMIN
   ============================================================ */

function renderAdminOverview(data) {
  const stats = data.stats || {};
  document.getElementById('admin-users-count').textContent = stats.users || 0;
  document.getElementById('admin-places-count').textContent = stats.places || 0;
  document.getElementById('admin-reviews-count').textContent = stats.reviews || 0;

  const usersList = document.getElementById('admin-users-list');
  const placesList = document.getElementById('admin-places-list');
  const reviewsList = document.getElementById('admin-reviews-list');

  usersList.innerHTML = (data.users || []).map((user) => `
    <li>${escapeHtml(`${user.first_name || ''} ${user.last_name || ''}`.trim() || user.name || 'User')} <span>${escapeHtml(user.email || '')}</span>${user.is_admin ? ' <strong>(admin)</strong>' : ''}</li>
  `).join('');

  placesList.innerHTML = (data.places || []).map((place) => {
    // Ensure we have a valid place ID from various possible field names
    const placeId = place.id || place.place_id || place.title || '';
    
    // Debug logging
    console.log('Admin rendering place:', { name: place.name, id: place.id, place_id: place.place_id, extractedId: placeId });
    
    // Only create an edit link if we have a non-empty, valid ID
    if (!placeId || placeId === '' || placeId === 'undefined' || placeId === 'null') {
      // No valid ID
      return `
        <li>
          <span>${escapeHtml(place.name)} — €${place.price}</span>
          <span class="muted">Edit unavailable</span>
        </li>
      `;
    }
    
    // Create a properly formatted edit URL
    const editUrl = `/create_edit_place.html?id=${encodeURIComponent(placeId)}`;
    console.log('Generated edit URL:', editUrl);

    return `
    <li>
      <span>${escapeHtml(place.name)} — €${place.price}</span>
      <a href="${editUrl}" data-place-id="${escapeHtml(placeId)}">Edit</a>
    </li>
  `;
  }).join('');

  reviewsList.innerHTML = (data.reviews || []).map((review) => `
    <li>
      <span>${escapeHtml(review.user || 'Anonymous')} on place ${escapeHtml(review.place_id)}: ${escapeHtml(review.text || '')}</span>
    </li>
  `).join('');
}

async function initAdminPage() {
  const panel = document.getElementById('admin-panel');
  if (!panel) return;

  const token = checkAuth();
  let user = getCurrentUser();
  if (!user) {
    try {
      user = await fetchCurrentUser(token);
      saveCurrentUser(user);
    } catch (error) {
      console.error('Failed to fetch current user:', error);
      panel.innerHTML = '<p class="empty-state">Please login again.</p>';
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

    if (usersRes.status === 403 || placesRes.status === 403) {
      panel.innerHTML = '<p class="empty-state">Admin access required.</p>';
      return;
    }

    if (!usersRes.ok) {
      const errorText = await usersRes.text();
      console.error(`Admin users endpoint failed with ${usersRes.status}:`, errorText);
    }

    if (!placesRes.ok) {
      const errorText = await placesRes.text();
      console.error(`Places endpoint failed with ${placesRes.status}:`, errorText);
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
    console.error('Admin page error:', error);
    panel.innerHTML = '<p class="empty-state">Could not load admin data.</p>';
  }
}

/* ============================================================
   ROUTER — detect which page we're on and init it
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  syncAuthUI();

  const path = window.location.pathname;
  console.log('=== ROUTER ===');
  console.log('Detected pathname:', path);

  if (path.endsWith('signup.html')) {
    console.log('-> Detected SIGNUP page');
    initSignupPage();
  }
  else if (path.endsWith('login.html')) {
    console.log('-> Detected LOGIN page');
    initLoginPage();
  }
  else if (path.endsWith('index.html') || path.endsWith('/') || path === '') {
    console.log('-> Detected INDEX page');
    initIndexPage();
  }
  else if (path.endsWith('place.html')) {
    console.log('-> Detected PLACE DETAILS page');
    initPlacePage();
  }
  else if (path.endsWith('add_review.html')) {
    console.log('-> Detected ADD REVIEW page');
    initAddReviewPage();
  }
  else if (path.endsWith('create_edit_place.html')) {
    console.log('-> Detected CREATE/EDIT PLACE page');
    initCreateEditPlacePage();
  }
  else if (path.endsWith('admin.html')) {
    console.log('-> Detected ADMIN page');
    initAdminPage();
  }
  else {
    console.log('-> No matching page detected for path:', path);
  }
});
