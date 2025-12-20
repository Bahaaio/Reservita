// Role guard: prevent agencies from accessing Events page
(function () {
    try {
        if (typeof getLoggedInUser === 'function') {
            const user = getLoggedInUser();
            const role = (user?.role || '').toString().trim().toLowerCase();
            if (user && role === 'agency') {
                window.__BLOCK_EVENTS_PAGE__ = true;
            }
        }
    } catch (e) {
        // ignore
    }
})();

function renderAgencyEventsBlockedMessage() {
    const container = document.querySelector('body > .container');
    if (!container) return;

    container.innerHTML = `
        <div style="padding-top: 120px; padding-bottom: 60px; text-align: center;">
            <div style="max-width: 700px; margin: 0 auto;">
                <h1 style="color: var(--text-white); font-size: 2rem; margin-bottom: 12px;">User account required</h1>
                <p style="color: var(--text-muted); font-size: 1.05rem; line-height: 1.6; margin-bottom: 22px;">
                    Make a user account to access this page.
                </p>
                <a href="signin.html" style="display: inline-flex; align-items: center; gap: 10px; background: var(--brand-dark); color: #fff; padding: 12px 18px; border-radius: 12px; text-decoration: none; font-weight: 700;">
                    <i class="fa-solid fa-user"></i>
                    Go to Sign In
                </a>
            </div>
        </div>
    `;
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (window.__BLOCK_EVENTS_PAGE__) {
            renderAgencyEventsBlockedMessage();
        }
        if (typeof updateRoleBasedNavLinks === 'function') {
            updateRoleBasedNavLinks();
        }
    });
} else {
    if (window.__BLOCK_EVENTS_PAGE__) {
        renderAgencyEventsBlockedMessage();
    }
    if (typeof updateRoleBasedNavLinks === 'function') {
        updateRoleBasedNavLinks();
    }
}

async function updateWishlistCount() {
    const countEl = document.getElementById('wishlistCount');
    if (!countEl) return;

    try {
        const token = localStorage.getItem('access_token');
        if (!token) {
            countEl.style.display = 'none';
            return;
        }

        const favorites = await FavoritesAPI.getFavorites();
        const count = Array.isArray(favorites) ? favorites.length : 0;
        countEl.textContent = count;
        countEl.style.display = count > 0 ? 'flex' : 'none';
    } catch (error) {
        console.error('Error updating wishlist count:', error);
        countEl.style.display = 'none';
    }
}

async function syncLocalFavoritesToBackend() {
    try {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        const userData = localStorage.getItem('currentUser');
        const user = userData ? JSON.parse(userData) : null;
        const userKey = user?.email || user?.name || 'unknown';

        const migrationKey = `favorites_migrated_v2_${userKey}`;
        if (localStorage.getItem(migrationKey) === '1') return;

        const localFavorites = JSON.parse(localStorage.getItem('favorites') || '[]');
        if (!Array.isArray(localFavorites) || localFavorites.length === 0) {
            localStorage.setItem(migrationKey, '1');
            return;
        }

        for (const eventId of localFavorites) {
            if (typeof eventId !== 'number' && typeof eventId !== 'string') continue;
            const idNum = parseInt(eventId, 10);
            if (Number.isNaN(idNum)) continue;
            try {
                await FavoritesAPI.addFavorite(idNum);
            } catch (e) {
                // ignore per-item failures
            }
        }

        localStorage.setItem(migrationKey, '1');
        localStorage.removeItem('favorites');
    } catch (error) {
        console.error('Error migrating local favorites:', error);
    }
}

async function renderAuthContainer() {
    const container = document.getElementById('authContainer');
    if (!container) return;

    const userData = localStorage.getItem('currentUser');
    const user = userData ? JSON.parse(userData) : null;

    if (user) {
        const role = (user?.role || '').toString().trim().toLowerCase();
        // Load avatar from database
        let avatarHtml = (user.name || '?').charAt(0).toUpperCase();
        try {
            const avatarBlob = await ProfileAPI.getAvatar();
            if (avatarBlob) {
                const avatarUrl = URL.createObjectURL(avatarBlob);
                avatarHtml = `<img src="${avatarUrl}" alt="${user.name}" style="width:100%; height:100%; object-fit:cover; border-radius:50%;">`;
            }
        } catch (error) {
            // Keep using initial letter
        }

    const roleLabel = role === 'agency' ? 'Agency' : 'User';
    const dashboardLink = role === 'agency' ? 'agency-dashboard.html' : 'user-dashboard.html';
        container.innerHTML = `
            <a href="wishlist.html" class="wishlist-icon" title="My Wishlist">
                <i class="fa-solid fa-heart"></i>
                <span id="wishlistCount" class="wishlist-count">0</span>
            </a>
            <a href="${dashboardLink}" class="logo-icon" title="Dashboard" style="width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700; text-decoration:none; color: white; overflow: hidden;">
                ${avatarHtml}
            </a>
            <div style="display:flex; flex-direction:column; line-height:1.1;">
                <span style="color:#fff; font-weight:700;">${user.name}</span>
                <span style="color: var(--text-muted); font-size:0.85rem;">${roleLabel}</span>
            </div>
            <button onclick="logout()" class="btn-nav-signin" style="background: var(--brand-dark); color:#fff; border:none; border-radius:12px; padding:8px 14px; display:flex; align-items:center; gap:6px; ">
                <i class="fa-solid fa-arrow-right-from-bracket"></i> Logout
            </button>
        `;
    } else {
        container.innerHTML = `
            <a href="wishlist.html" class="wishlist-icon" title="My Wishlist">
                <i class="fa-solid fa-heart"></i>
                <span id="wishlistCount" class="wishlist-count">0</span>
            </a>
            <div id="userProfile" class="logo-icon" style="width: 32px; height: 32px; border-radius: 50%; cursor: pointer;" title="User Profile">
                <i class="fa-solid fa-user"></i>
            </div>
            <a id="signInBtn" href="signin.html" class="btn-nav-signin">Sign In</a>
        `;
    }
    await syncLocalFavoritesToBackend();
    await updateWishlistCount();

    if (typeof updateRoleBasedNavLinks === 'function') {
        updateRoleBasedNavLinks();
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderAuthContainer);
} else {
    renderAuthContainer();
}
