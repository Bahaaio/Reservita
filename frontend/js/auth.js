/* --- Authentication & User Management --- */

async function loadAndSaveCurrentUser() {
    try {
        const userProfile = await ProfileAPI.getProfile();
        const userData = {
            name: userProfile.full_name,
            email: userProfile.email,
            phone: userProfile.phone_number,
            role: userProfile.is_agency ? 'agency' : 'user',
            loginTime: new Date().getTime()
        };
        localStorage.setItem('currentUser', JSON.stringify(userData));
        return userData;
    } catch (error) {
        console.error('Failed to load user profile:', error);
        return null;
    }
}

function saveUser(name, email, role, phone = '') {
    const userData = {
        name: name,
        email: email,
        phone: phone,
        role: role,
        loginTime: new Date().getTime()
    };
    localStorage.setItem('currentUser', JSON.stringify(userData));
}

function getLoggedInUser() {
    const userData = localStorage.getItem('currentUser');
    return userData ? JSON.parse(userData) : null;
}

function getNormalizedRole(user) {
    return (user?.role || '').toString().trim().toLowerCase();
}

function isLoggedIn() {
    const token = getAuthToken();
    if (!token || isTokenExpired()) {
        return false;
    }
    return getLoggedInUser() !== null;
}

function logout() {
    AuthAPI.logout();
    localStorage.removeItem('currentUser');
    window.location.href = 'index.html'; // Redirect to home after logout
}

function getUserAvatar(name, photo = null) {
    if (photo) {
        return `<img src="${photo}" alt="${name}" style="width:100%; height:100%; object-fit:cover; border-radius:50%;">`;
    }
    const firstLetter = name.charAt(0).toUpperCase();
    return firstLetter;
}

async function loadUserAvatarFromDB() {
    try {
        const avatarBlob = await ProfileAPI.getAvatar();
        if (avatarBlob) {
            return URL.createObjectURL(avatarBlob);
        }
    } catch (error) {
        // No avatar or error loading it
        return null;
    }
    return null;
}

function protectDashboard(requiredRole) {
    const user = getLoggedInUser();
    
    if (!user) {
        window.location.href = 'signin.html';
        return;
    }
    
    // If role is specified, check if user has correct role
    if (requiredRole) {
        if (getNormalizedRole(user) !== requiredRole) {
            // Redirect to correct dashboard
            if (getNormalizedRole(user) === 'agency') {
                window.location.href = 'agency-dashboard.html';
            } else {
                window.location.href = 'user-dashboard.html';
            }
            return;
        }
    }
}

/**
 * Initialize navbar for Dashboard pages (looks for 'userInfo')
 */
async function initializeUserNavbar() {
    const user = getLoggedInUser();
    if (!user) return;
    
    const userInfoContainer = document.getElementById('userInfo');
    if (!userInfoContainer) return;
    
    // Load avatar from database
    const avatarUrl = await loadUserAvatarFromDB();
    const avatar = getUserAvatar(user.name, avatarUrl);
    
    // Extract first name only
    const firstName = user.name.split(' ')[0];
    
    // Uses dashboard specific class .user-card from dashboard.css
    const role = getNormalizedRole(user);
    userInfoContainer.innerHTML = `
        <div class="user-card">
            <a href="profile.html" class="user-avatar" style="text-decoration:none; cursor:pointer; color:white;">${avatar}</a>
            <div class="user-details">
                <div class="user-name">${firstName}</div>
                <div class="user-role">${role === 'agency' ? 'Agency' : 'User'}</div>
            </div>
            <button onclick="logout()" class="logout-btn">
                <i class="fa-solid fa-sign-out-alt"></i>
                Logout
            </button>
        </div>
    `;

    updateRoleBasedNavLinks();
}

/**
 * Initialize navbar for Home/Index page (looks for 'navAuth' and 'mobileAuth')
 */
async function initHomeNav() {
    const user = getLoggedInUser();
    const navAuth = document.getElementById('navAuth');
    const mobileAuth = document.getElementById('mobileAuth');

    if (user) {
        // Load avatar from database
        const avatarUrl = await loadUserAvatarFromDB();
        
        // --- 1. Desktop Nav: Show User Profile (Matches Dashboard Style) ---
        if (navAuth) {
            const avatar = getUserAvatar(user.name, avatarUrl);
            const dashboardLink = getNormalizedRole(user) === 'agency' ? 'agency-dashboard.html' : 'user-dashboard.html';
            
            // Extract first name only
            const firstName = user.name.split(' ')[0];

            navAuth.innerHTML = `
                <div class="nav-user-widget">
                    <a href="profile.html" class="nav-user-avatar">${avatar}</a>
                    <div class="nav-user-details">
                        <div class="nav-user-name">${firstName}</div>
                        <div class="nav-user-role">${getNormalizedRole(user) === 'agency' ? 'Agency' : 'User'}</div>
                    </div>
                    <button onclick="logout()" class="nav-logout-btn">
                        <i class="fa-solid fa-arrow-right-from-bracket"></i> Logout
                    </button>
                </div>
            `;
        }

        // --- 2. Mobile Nav: Show Dashboard Link + Logout ---
        if (mobileAuth) {
            const dashboardLink = getNormalizedRole(user) === 'agency' ? 'agency-dashboard.html' : 'user-dashboard.html';
            mobileAuth.innerHTML = `
                <div style="border-top: 1px solid rgba(255,255,255,0.1); margin-top:10px; padding-top:10px;">
                    <a href="${dashboardLink}" class="mobile-link" style="color: #ec4899; font-weight:700;">
                        <i class="fa-solid fa-user-circle"></i> Dashboard
                    </a>
                    <button onclick="logout()" class="mobile-link" style="background:none; text-align:left; width:100%; color: #94a3b8;">
                        <i class="fa-solid fa-sign-out-alt"></i> Logout
                    </button>
                </div>
            `;
        }

        updateRoleBasedNavLinks();

    } else {
        // --- User NOT Logged In: Show Sign In Buttons ---
        
        if (navAuth) {
            navAuth.innerHTML = `<a href="signin.html" class="btn-primary">Sign In</a>`;
        }

        if (mobileAuth) {
            mobileAuth.innerHTML = `<a href="signin.html" class="mobile-link" style="color: var(--brand-primary);">Sign In</a>`;
        }
    }
}

function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileMenu) {
        mobileMenu.classList.toggle('hidden');
    }
}

function updateRoleBasedNavLinks() {
    const user = getLoggedInUser();
    if (!user) return;

    // Find nav groups that contain site links (nav-link anchors)
    const navGroups = Array.from(document.querySelectorAll('.nav-links'))
        .filter(group => group.querySelector('a.nav-link'));

    if (navGroups.length === 0) return;

    const isAgency = getNormalizedRole(user) === 'agency';
    const desired = isAgency
        ? { href: 'agency-dashboard.html#analytics', text: 'Analytics' }
        : { href: 'user-dashboard.html', text: 'My Tickets' };

    for (const group of navGroups) {
        const links = Array.from(group.querySelectorAll('a.nav-link'));

        // Look for an existing role link (My Tickets or Analytics) and update it
        const roleLink = links.find(a => {
            const href = (a.getAttribute('href') || '').toLowerCase();
            const text = (a.textContent || '').toLowerCase().trim();
            return href.includes('user-dashboard.html') || href.includes('agency-dashboard.html') ||
                text === 'my tickets' || text === 'analytics';
        });

        if (roleLink) {
            roleLink.setAttribute('href', desired.href);
            roleLink.textContent = desired.text;
        } else {
            // Insert after the Events link if present, else append
            const eventsLink = links.find(a => (a.getAttribute('href') || '').toLowerCase().includes('events.html'));
            const newLink = document.createElement('a');
            newLink.className = 'nav-link';
            newLink.setAttribute('href', desired.href);
            newLink.textContent = desired.text;

            if (eventsLink && eventsLink.parentElement === group) {
                eventsLink.insertAdjacentElement('afterend', newLink);
            } else {
                group.appendChild(newLink);
            }
        }
    }

    // Also update mobile menu links (index/about pages)
    const mobileLinks = Array.from(document.querySelectorAll('.mobile-menu a.mobile-link'));
    const mobileRoleLink = mobileLinks.find(a => {
        const href = (a.getAttribute('href') || '').toLowerCase();
        const text = (a.textContent || '').toLowerCase().trim();
        return href.includes('user-dashboard.html') || href.includes('agency-dashboard.html') ||
            text === 'my tickets' || text === 'analytics';
    });

    if (mobileRoleLink) {
        mobileRoleLink.setAttribute('href', desired.href);
        mobileRoleLink.textContent = desired.text;
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateRoleBasedNavLinks);
} else {
    updateRoleBasedNavLinks();
}