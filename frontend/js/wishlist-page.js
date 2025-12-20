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

async function loadWishlist() {
    const container = document.getElementById('wishlistContainer');
    const clearAllBtn = document.getElementById('clearAllBtn');
    const subtitle = document.getElementById('wishlistSubtitle');

    try {
        await syncLocalFavoritesToBackend();
        // Fetch favorites from backend
        const favorites = await FavoritesAPI.getFavorites();

        if (!favorites || favorites.length === 0) {
            container.innerHTML = `
                <div class="empty-state-modern">
                    <div class="empty-illustration">
                        <i class="fa-solid fa-heart-crack"></i>
                    </div>
                    <h3>Your wishlist is empty</h3>
                    <p>Start exploring events and save your favorites by clicking the heart icon on any event card.</p>
                    <a href="events.html" class="btn-empty-state">
                        <i class="fa-solid fa-compass"></i>
                        Browse Events
                    </a>
                </div>
            `;
            clearAllBtn.style.display = 'none';
            return;
        }

        subtitle.textContent = `${favorites.length} saved event${favorites.length !== 1 ? 's' : ''}`;
        clearAllBtn.style.display = 'flex';

        container.innerHTML = favorites.map(event => {
            const eventDate = new Date(event.starts_at);
            const dateStr = eventDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
            const priceDisplay = `$${event.ticket_price}`;

            // Get banner URL
            const bannerUrl = event.banner_ids && event.banner_ids.length > 0
                ? `http://127.0.0.1:8000/api/v1/events/banners/${event.banner_ids[0]}`
                : 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600';

            return `
                <div class="event-card">
                    <div class="card-img-wrapper">
                        <img src="${bannerUrl}" class="card-img" alt="${event.title}" onerror="this.src='https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600'">
                        <div class="card-badge">${event.category}</div>
                        <button class="favorite-btn active" onclick="removeFromWishlist(${event.id})" title="Remove from wishlist">
                            <i class="fa-solid fa-heart"></i>
                        </button>
                    </div>
                    <div class="card-body">
                        <div class="event-meta">${dateStr}</div>
                        <h3 class="event-title">${event.title}</h3>
                        <div class="event-info">
                            <i class="fa-solid fa-location-dot"></i> ${event.city}
                        </div>
                        <div class="card-footer">
                            <span class="price-tag">${priceDisplay}</span>
                            <a href="event-details.html?id=${event.id}" class="btn-details">View Details <i class="fa-solid fa-arrow-right"></i></a>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading wishlist:', error);
        container.innerHTML = `
            <div class="empty-state-modern">
                <div class="empty-illustration">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                </div>
                <h3>Error loading wishlist</h3>
                <p>${error.message}</p>
                <a href="events.html" class="btn-empty-state">
                    <i class="fa-solid fa-compass"></i>
                    Browse Events
                </a>
            </div>
        `;
    }
}

async function removeFromWishlist(eventId) {
    try {
        await FavoritesAPI.removeFavorite(eventId);

        // Reload the wishlist
        await loadWishlist();

        // Show notification
        showNotification('Removed from wishlist');
    } catch (error) {
        console.error('Error removing from wishlist:', error);
        showNotification('Failed to remove from wishlist: ' + (error.message || 'Unknown error'));
    }
}

async function clearAllWishlist() {
    if (confirm('Are you sure you want to remove all events from your wishlist?')) {
        try {
            await FavoritesAPI.clearAllFavorites();
            await loadWishlist();
            showNotification('Wishlist cleared');
        } catch (error) {
            console.error('Error clearing wishlist:', error);
            showNotification('Failed to clear wishlist: ' + (error.message || 'Unknown error'));
        }
    }
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: linear-gradient(135deg, var(--brand-dark), var(--brand-primary));
        color: white;
        padding: 15px 25px;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(236, 72, 153, 0.4);
        z-index: 30000;
        font-weight: 600;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 2000);
}

// Load wishlist on page load
document.addEventListener('DOMContentLoaded', loadWishlist);
