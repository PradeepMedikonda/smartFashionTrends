// API Configuration
const API_BASE_URL = 'http://localhost:5000';
let authToken = localStorage.getItem('authToken');
let currentUser = localStorage.getItem('currentUser');

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    if (authToken && currentUser) {
        showApp();
        loadRecommendations();
    }
});

// Auth Functions
function showTab(tab) {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const tabs = document.querySelectorAll('.tab-btn');

    tabs.forEach(btn => btn.classList.remove('active'));
    
    if (tab === 'login') {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
        tabs[0].classList.add('active');
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
        tabs[1].classList.add('active');
    }
}

async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');

    if (!username || !password) {
        showError(errorDiv, 'Please enter username and password');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            authToken = data.token;
            currentUser = data.username;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', currentUser);
            showApp();
            loadRecommendations();
        } else {
            showError(errorDiv, data.error || 'Login failed');
        }
    } catch (error) {
        showError(errorDiv, 'Unable to connect to server. Make sure the API is running.');
    }
}

async function register() {
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const errorDiv = document.getElementById('register-error');

    if (!username || !email || !password) {
        showError(errorDiv, 'Please fill in all fields');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            authToken = data.token;
            currentUser = data.username;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', currentUser);
            showApp();
            loadRecommendations();
        } else {
            showError(errorDiv, data.error || 'Registration failed');
        }
    } catch (error) {
        showError(errorDiv, 'Unable to connect to server. Make sure the API is running.');
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('app-section').style.display = 'none';
    document.getElementById('user-info').style.display = 'none';
}

function showApp() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('app-section').style.display = 'block';
    document.getElementById('user-info').style.display = 'block';
    document.getElementById('username-display').textContent = `👤 ${currentUser}`;
}

// Navigation
function showSection(section) {
    const sections = ['recommendations', 'trends', 'preferences'];
    const navBtns = document.querySelectorAll('.nav-btn');

    sections.forEach(s => {
        document.getElementById(`${s}-section`).style.display = 'none';
    });

    navBtns.forEach(btn => btn.classList.remove('active'));

    document.getElementById(`${section}-section`).style.display = 'block';
    const btnIndex = sections.indexOf(section);
    if (btnIndex !== -1) {
        navBtns[btnIndex].classList.add('active');
    }

    // Load data for the section
    if (section === 'recommendations') {
        loadRecommendations();
    } else if (section === 'trends') {
        loadTrends();
    } else if (section === 'preferences') {
        loadPreferences();
    }
}

// Recommendations
async function loadRecommendations() {
    const container = document.getElementById('recommendations-list');
    container.innerHTML = '<div class="loading">Loading recommendations...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/recommendations?top_n=12`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        const data = await response.json();

        if (response.ok) {
            displayRecommendations(data.recommendations);
        } else {
            container.innerHTML = `<div class="empty-state"><p>❌ ${data.error}</p></div>`;
        }
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><p>❌ Unable to load recommendations</p></div>';
    }
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations-list');

    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>No recommendations available yet.</p>
                <p>Try interacting with some items first!</p>
            </div>
        `;
        return;
    }

    container.innerHTML = recommendations.map(item => `
        <div class="item-card">
            <h3>${item.name || `Item ${item.item_id}`}</h3>
            <div class="item-detail"><strong>Category:</strong> ${item.category || 'N/A'}</div>
            <div class="item-detail"><strong>Style:</strong> ${item.style || 'N/A'}</div>
            <div class="item-detail"><strong>Color:</strong> ${item.color || 'N/A'}</div>
            <div class="item-detail"><strong>Brand:</strong> ${item.brand || 'N/A'}</div>
            <div class="item-detail"><strong>Price:</strong> $${item.price || '0.00'}</div>
            <span class="item-score">Score: ${item.score ? item.score.toFixed(2) : 'N/A'}</span>
            <div class="item-actions">
                <button class="action-btn like-btn" onclick="submitFeedback(${item.item_id}, 'like')">
                    ❤️ Like
                </button>
                <button class="action-btn cart-btn" onclick="submitFeedback(${item.item_id}, 'cart')">
                    🛒 Cart
                </button>
                <button class="action-btn wishlist-btn" onclick="submitFeedback(${item.item_id}, 'wishlist')">
                    ⭐ Wishlist
                </button>
            </div>
        </div>
    `).join('');
}

async function submitFeedback(itemId, interactionType) {
    const ratingMap = {
        'like': 4.0,
        'cart': 4.5,
        'wishlist': 4.0,
        'purchase': 5.0
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/recommendations/feedback`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                item_id: itemId,
                interaction_type: interactionType,
                rating: ratingMap[interactionType] || 4.0
            })
        });

        if (response.ok) {
            alert(`✅ ${interactionType.charAt(0).toUpperCase() + interactionType.slice(1)} recorded!`);
            loadRecommendations(); // Refresh recommendations
        }
    } catch (error) {
        alert('❌ Failed to record feedback');
    }
}

// Trends
async function loadTrends() {
    const days = document.getElementById('trend-days').value;
    const container = document.getElementById('trends-list');
    container.innerHTML = '<div class="loading">Loading trends...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/trends?days=${days}`);
        const data = await response.json();

        if (response.ok) {
            displayTrends(data.trends);
        } else {
            container.innerHTML = `<div class="empty-state"><p>❌ ${data.error}</p></div>`;
        }
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><p>❌ Unable to load trends</p></div>';
    }
}

function displayTrends(trends) {
    const container = document.getElementById('trends-list');

    if (!trends || Object.keys(trends).length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No trends data available</p></div>';
        return;
    }

    let html = '';

    for (const [category, items] of Object.entries(trends)) {
        html += `
            <div class="trend-category">
                <h3>📊 ${category.charAt(0).toUpperCase() + category.slice(1)}</h3>
                <div class="trend-items">
                    ${Object.entries(items).map(([key, value]) => `
                        <div class="trend-tag">
                            <span class="trend-value">${key}</span>
                            <span class="trend-score">${typeof value === 'number' ? value.toFixed(1) : value}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

async function loadSeasonalTrends(season) {
    const container = document.getElementById('seasonal-trends-list');
    container.innerHTML = '<div class="loading">Loading seasonal trends...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/trends/seasonal/${season}`);
        const data = await response.json();

        if (response.ok) {
            container.innerHTML = `
                <div class="trend-category">
                    <h3>${season.charAt(0).toUpperCase() + season.slice(1)} Trends</h3>
                    <p>${data.count} trending items for ${season}</p>
                    ${data.trends && data.trends.length > 0 ? `
                        <div class="items-grid" style="margin-top: 20px;">
                            ${data.trends.slice(0, 6).map(item => `
                                <div class="item-card">
                                    <h3>${item.name || `Item ${item.id}`}</h3>
                                    <div class="item-detail"><strong>Category:</strong> ${item.category || 'N/A'}</div>
                                    <div class="item-detail"><strong>Style:</strong> ${item.style || 'N/A'}</div>
                                    <div class="item-detail"><strong>Color:</strong> ${item.color || 'N/A'}</div>
                                </div>
                            `).join('')}
                        </div>
                    ` : '<p style="margin-top: 10px;">No items found for this season</p>'}
                </div>
            `;
        } else {
            container.innerHTML = `<div class="empty-state"><p>❌ ${data.error}</p></div>`;
        }
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><p>❌ Unable to load seasonal trends</p></div>';
    }
}

// Preferences
async function loadPreferences() {
    const container = document.getElementById('preferences-list');
    container.innerHTML = '<div class="loading">Loading preferences...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/user/preferences`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        const data = await response.json();

        if (response.ok) {
            displayPreferences(data.preferences);
        } else {
            container.innerHTML = `<div class="empty-state"><p>❌ ${data.error}</p></div>`;
        }
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><p>❌ Unable to load preferences</p></div>';
    }
}

function displayPreferences(preferences) {
    const container = document.getElementById('preferences-list');

    if (!preferences || preferences.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>No preferences set yet.</p>
                <p>Interact with items to build your preferences!</p>
            </div>
        `;
        return;
    }

    container.innerHTML = preferences.map(pref => `
        <div class="preference-item">
            <div class="preference-info">
                <div class="preference-key">${pref.key}</div>
                <div class="preference-value">${pref.value}</div>
            </div>
            <span class="preference-weight">Weight: ${pref.weight.toFixed(2)}</span>
        </div>
    `).join('');
}

// Utility Functions
function showError(element, message) {
    element.textContent = message;
    element.classList.add('show');
    setTimeout(() => {
        element.classList.remove('show');
    }, 5000);
}
