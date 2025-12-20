// Events data loader and filters
// Fetches events from backend API

let allEvents = [];
let currentPage = 1;
let totalPages = 1;

// Default placeholder image for events without banners
const defaultEventImage = "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600";

// Function to get banner URL from backend
function getBannerUrl(bannerId) {
    if (!bannerId) return defaultEventImage;
    return `${API_BASE_URL}/api/v1/events/banners/${bannerId}`;
}

// Function to format event data from backend to frontend format
function formatEventData(backendEvent) {
    const startsAt = new Date(backendEvent.starts_at);
    const endsAt = new Date(backendEvent.ends_at);
    
    const startTime = startsAt.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    const endTime = endsAt.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    
    const categoryKey = backendEvent.category || 'other';
    const categoryLabel = categoryKey.charAt(0).toUpperCase() + categoryKey.slice(1);

    const ticketPrice = Number(backendEvent.ticket_price ?? 0);
    const safePrice = Number.isFinite(ticketPrice) ? ticketPrice : 0;

    return {
        id: backendEvent.id,
        title: backendEvent.title,
        city: backendEvent.city,
        category: categoryKey,
        categoryLabel,
        price: safePrice,
        vipPrice: backendEvent.vip_ticket_price,
        dateString: backendEvent.starts_at,
        time: `${startTime} - ${endTime}`,
        image: backendEvent.banner_ids.length > 0 ? getBannerUrl(backendEvent.banner_ids[0]) : defaultEventImage,
        venue: backendEvent.venue,
        venueAddress: backendEvent.address,
        description: backendEvent.description,
        longDescription: backendEvent.description,
        galleryImages: backendEvent.banner_ids.map(id => getBannerUrl(id)),
        averageRating: backendEvent.average_rating,
        isFavorited: backendEvent.is_favorited
    };
}

function normalizeCityValue(value) {
    return (value || '')
        .toString()
        .toLowerCase()
        .replace(/\s+/g, ' ')
        .replace(/,\s*[a-z]{2}$/i, '')
        .trim();
}

// Load events from backend API
async function loadEvents(page = 1, size = 50) {
    try {
        const response = await EventsAPI.listAllEvents(page, size);
        if (!response || !response.items) {
            throw new Error('Invalid response from server');
        }
        allEvents = response.items.map(formatEventData);
        currentPage = response.page;
        totalPages = response.pages;
        return allEvents;
    } catch (error) {
        console.error('Failed to load events:', error);
        
        // Show error message to user
        const container = document.getElementById('eventsContainer');
        if (container) {
            container.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 40px;">
                    <div style="color: #ef4444; margin-bottom: 20px;">
                        <i class="fa-solid fa-exclamation-triangle" style="font-size: 3rem;"></i>
                    </div>
                    <h3 style="color: white; margin-bottom: 10px;">Failed to Load Events</h3>
                    <p style="color: var(--text-muted); margin-bottom: 20px;">${error.message}</p>
                    <button onclick="location.reload()" style="background: var(--brand-dark); color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer;">
                        Try Again
                    </button>
                </div>
            `;
        }
        
        allEvents = [];
        return [];
    }
}

function getURLParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

function applyURLSearchParameter() {
    const searchParam = getURLParameter('search');
    const cityParam = getURLParameter('city');
    const categoriesParam = getURLParameter('categories');

    if (cityParam) {
        const citySelect = document.getElementById('citySelect');
        if (citySelect) {
            // If value doesn't exist in options, default to All
            const hasOption = Array.from(citySelect.options).some(o => o.value === cityParam);
            citySelect.value = hasOption ? cityParam : 'All';
        }
        // If arriving with only a city filter, apply it
        if (!searchParam) {
            applyFilters();
            if (cityParam && cityParam !== 'All') {
                showSearchNotification(`Filtered by city:  "${cityParam}"`);
            }
        }
    }

    if (searchParam) {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = searchParam;
        }

        // When arriving from index search, avoid hiding results due to stale sidebar filters
        const priceMinEl = document.getElementById('priceMin');
        const priceMaxEl = document.getElementById('priceMax');
        const dateStartEl = document.getElementById('dateStart');
        const dateEndEl = document.getElementById('dateEnd');

        if (priceMinEl) priceMinEl.value = '0';
        if (priceMaxEl) priceMaxEl.value = '';
        if (dateStartEl) dateStartEl.value = '';
        if (dateEndEl) dateEndEl.value = '';

        // Clear category filters (no category restriction)
        document.querySelectorAll('#categoryFilters input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });

        applyFilters();
        showSearchNotification(`Showing results for:  "${searchParam}"`);
    }

    // Apply categories from URL if provided
    if (categoriesParam) {
        const selectedCats = categoriesParam.split(',').map(c => c.trim().toLowerCase()).filter(Boolean);
        const checkboxes = document.querySelectorAll('#categoryFilters input[type="checkbox"]');
        checkboxes.forEach(cb => {
            cb.checked = selectedCats.includes(cb.value.toLowerCase());
        });
        applyFilters();
        if (selectedCats.length > 0) {
            const label = selectedCats.map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(', ');
            showSearchNotification(`Filtered by category:  "${label}"`);
        }
    }
}

function showSearchNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: var(--brand-dark);
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(236, 72, 153, 0.4);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function renderEvents(events) {
    const container = document.getElementById('eventsContainer');
    const countLabel = document.getElementById('resultsCount');

    if (countLabel) {
        countLabel.innerHTML = `Showing <strong>${events.length}</strong> event${events.length !== 1 ? 's' : ''}`;
    }

    container.innerHTML = '';

    if (events.length === 0) {
        container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">No events found matching your filters.</div>`;
        return;
    }

    let html = '';
    
    events.forEach(ev => {
        const eventDate = new Date(ev.dateString);
        const dateStr = eventDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        const priceDisplay = `$${ev.price}`;
        const isFavorite = ev.isFavorited || false;
        const heartIcon = isFavorite ? 'fa-solid fa-heart' : 'fa-regular fa-heart';

        html += `
        <div class="event-card">
            <div class="card-img-wrapper">
                <img src="${ev.image}" class="card-img" alt="${ev.title}" onerror="this.src='https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600'">
                <div class="card-badge">${ev.categoryLabel || ev.category}</div>
                <button class="favorite-btn" onclick="toggleFavorite(event, ${ev.id})" title="Add to favorites">
                    <i class="${heartIcon}"></i>
                </button>
            </div>
            <div class="card-body">
                <div class="event-meta">${dateStr} ${ev.time ? '• ' + ev.time.split(' - ')[0] : ''}</div>
                <h3 class="event-title">${ev.title}</h3>
                <div class="event-info">
                    <i class="fa-solid fa-location-dot"></i> ${ev.city}
                </div>
                <div class="card-footer">
                    <span class="price-tag">${priceDisplay}</span>
                    <a href="event-details.html?id=${ev.id}" class="btn-details">View Details <i class="fa-solid fa-arrow-right"></i></a>
                </div>
            </div>
        </div>
        `;
    });
    container.innerHTML = html;
}

function applyFilters() {
    const btn = document.querySelector('.btn-apply');
    const originalText = btn.innerText;
    btn.innerText = "Applying...";
    btn.style.opacity = "0.7";

    setTimeout(() => {
        const searchTerm = (document.getElementById('searchInput').value || '').toLowerCase();
        const selectedCity = document.getElementById('citySelect').value;

        const minPriceRaw = document.getElementById('priceMin').value;
        const maxPriceRaw = document.getElementById('priceMax').value;
        const minPrice = minPriceRaw === '' ? 0 : (parseInt(minPriceRaw, 10) || 0);
        const maxPrice = maxPriceRaw === '' ? Number.POSITIVE_INFINITY : (parseInt(maxPriceRaw, 10) || Number.POSITIVE_INFINITY);

        const startDate = document.getElementById('dateStart').valueAsDate;
        const endDate = document.getElementById('dateEnd').valueAsDate;

        document.querySelector('input[name="priceType"]');
        const checkedCats = Array.from(document.querySelectorAll('#categoryFilters input:checked')).map(cb => cb.value);

        let filtered = allEvents.filter(ev => {
            const searchMatch = searchTerm === '' ||
                ev.title.toLowerCase().includes(searchTerm) ||
                ev.city.toLowerCase().includes(searchTerm) ||
                ev.category.toLowerCase().includes(searchTerm);

            if (!searchMatch) return false;
            if (selectedCity !== 'All' && normalizeCityValue(ev.city) !== normalizeCityValue(selectedCity)) return false;
            if (checkedCats.length > 0 && !checkedCats.includes(ev.category)) return false;
            if (ev.price < minPrice || ev.price > maxPrice) return false;

            const evDate = new Date(ev.dateString);
            if (startDate && evDate < startDate) return false;
            if (endDate && evDate > endDate) return false;

            return true;
        });

        const sortType = document.getElementById('sortSelect').value;
        if (sortType === 'date') filtered.sort((a, b) => new Date(b.dateString) - new Date(a.dateString));
        else if (sortType === 'price_asc') filtered.sort((a, b) => a.price - b.price);
        else if (sortType === 'price_desc') filtered.sort((a, b) => b.price - a.price);

        renderEvents(filtered);
        btn.innerText = originalText;
        btn.style.opacity = "1";
    }, 300);
}

async function toggleFavorite(event, eventId) {
    event.stopPropagation();
    event.preventDefault();
    
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (!token) {
        if (typeof showNotification === 'function') {
            showNotification('Please log in to add favorites');
            setTimeout(() => {
                window.location.href = 'signin.html';
            }, 800);
        } else {
            window.location.href = 'signin.html';
        }
        return;
    }
    
    const heartIcon = event.currentTarget.querySelector('i');
    const isFavorited = heartIcon.classList.contains('fa-solid');
    
    try {
        if (isFavorited) {
            // Remove from favorites
            await FavoritesAPI.removeFavorite(eventId);
            heartIcon.className = 'fa-regular fa-heart';
        } else {
            // Add to favorites
            await FavoritesAPI.addFavorite(eventId);
            heartIcon.className = 'fa-solid fa-heart';
            
            // Add animation
            heartIcon.style.animation = 'heartBeat 0.3s ease';
            setTimeout(() => {
                heartIcon.style.animation = '';
            }, 300);
        }
        
        // Update wishlist count if function exists
        if (typeof updateWishlistCount === 'function') {
            updateWishlistCount();
        }
    } catch (error) {
        console.error('Error toggling favorite:', error);
        if (typeof showNotification === 'function') {
            showNotification('Failed to update favorites: ' + (error.message || 'Unknown error'));
        }
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    if (window.__BLOCK_EVENTS_PAGE__) {
        return;
    }
    // Show loading state
    const container = document.getElementById('eventsContainer');
    if (container) {
        container.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-muted);"><i class="fa-solid fa-spinner fa-spin"></i> Loading events...</div>';
    }
    
    // Load events from API
    await loadEvents();
    
    // Render events
    renderEvents(allEvents);
    applyURLSearchParameter();
});

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn { from { transform: translateX(400px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(400px); opacity: 0; } }
`;
document.head.appendChild(style);

function showNotification(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: linear-gradient(135deg, var(--brand-dark), var(--brand-primary));
        color: white;
        padding: 12px 20px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.6);
        z-index: 30000;
        font-weight: 600;
        animation: slideIn 0.25s ease-out;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.25s ease-in';
        setTimeout(() => toast.remove(), 250);
    }, 2000);
}
