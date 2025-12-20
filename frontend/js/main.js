/* --- Events Data from API --- */
let events = [];

/* --- State Variables --- */
let currentCategory = "All";
let currentSearch = "";
let selectedEvent = null;

/* --- Load Events from Backend --- */
async function loadHomePageEvents() {
    try {
        const response = await EventsAPI.listAllEvents(1, 6); // Get first 6 events for homepage
        if (!response || !response.items) {
            throw new Error('Invalid response from server');
        }
        events = response.items.map(event => {
            const startsAt = new Date(event.starts_at);
            return {
                id: event.id,
                title: event.title,
                date: startsAt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
                time: startsAt.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
                location: `${event.venue}, ${event.city}`,
                price: event.ticket_price,
                category: event.category.charAt(0).toUpperCase() + event.category.slice(1),
                image: event.banner_ids.length > 0 ? `${API_BASE_URL}/api/v1/events/banners/${event.banner_ids[0]}` : 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600',
                attendees: 0
            };
        });
        return events;
    } catch (error) {
        console.error('Failed to load events:', error);
        
        // Show error in container
        const container = document.getElementById("eventsGrid");
        if (container) {
            container.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 40px;">
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
        
        events = [];
        return [];
    }
}

/* --- Initialize --- */
document.addEventListener("DOMContentLoaded", async function() {
    // Show loading state
    const container = document.getElementById("eventsGrid");
    if (container) {
        container.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted);"><i class="fa-solid fa-spinner fa-spin"></i> Loading events...</div>';
    }
    
    // Load events from API
    await loadHomePageEvents();
    
    // Render events
    renderEvents();
    setupEventListeners();
    setupMobileMenu();
    setupNavbarScroll();
});

/* --- Event Listeners Setup --- */
function setupEventListeners() {
    const searchInput = document.getElementById("searchInput");
    const searchBtn = document.getElementById("searchBtn");
    const resetBtn = document.getElementById("resetBtn");
    const modalBackdrop = document.getElementById("bookingModal");
    const locationSelect = document.querySelector('.location-select');
    
    if (searchInput) {
        searchInput.addEventListener("input", function(e) {
            currentSearch = e.target.value.toLowerCase();
            renderEvents();
        });
        
        // Allow Enter key to trigger search
        searchInput.addEventListener("keypress", function(e) {
            if (e.key === "Enter") {
                filterEvents();
            }
        });
    }
    
    if (searchBtn) {
        searchBtn.addEventListener("click", filterEvents);
    }
    
    if (resetBtn) {
        resetBtn.addEventListener("click", resetFilters);
    }
    
    if (modalBackdrop) {
        modalBackdrop.addEventListener("click", function(e) {
            if (e.target === modalBackdrop) {
                closeModal();
            }
        });
    }

    // Optional UX: auto-redirect when city changes (no search needed)
    if (locationSelect) {
        locationSelect.addEventListener('change', function() {
            const city = locationSelect.value;
            if (city && city !== 'All') {
                const params = new URLSearchParams();
                params.set('city', city);
                window.location.href = `events.html?${params.toString()}`;
            }
        });
    }
}

function setupMobileMenu() {
    const mobileMenuBtn = document.querySelector(".mobile-menu-btn");
    const mobileMenu = document.querySelector(".mobile-menu");
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener("click", function() {
            mobileMenu.classList.toggle("hidden");
        });
    }
}

/* --- Navbar Scroll Behavior --- */
function setupNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    function onScroll() {
        if (window.scrollY > 20) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
}

/* --- Render Events --- */
function renderEvents() {
    const container = document.getElementById("eventsGrid");
    if (!container) return;
    
    let filtered = events.filter(event => {
        const matchCategory = currentCategory === "All" || event.category === currentCategory;
        const matchSearch = event.title.toLowerCase().includes(currentSearch) || 
                          event.location.toLowerCase().includes(currentSearch);
        return matchCategory && matchSearch;
    });
    
    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="no-results" style="grid-column: 1 / -1;">
                <div class="no-results-icon">
                    <i class="fas fa-search"></i>
                </div>
                <div class="no-results-text">No events found matching your search.</div>
                <button class="btn-clear" onclick="resetFilters()">Clear filters</button>
            </div>
        `;
        return;
    }
    
    const loggedIn = (typeof isLoggedIn === 'function') ? isLoggedIn() : false;

    container.innerHTML = filtered.map(event => `
        <div class="event-card">
            <div class="card-image-wrapper">
                <img src="${event.image}" alt="${event.title}" class="card-image" onerror="this.src='https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600'">
                <div class="card-badge">${event.category}</div>
            </div>
            <div class="card-content">
                <div class="event-meta">${event.date} • ${event.time}</div>
                <h3 class="event-title">${event.title}</h3>
                <div class="event-location">
                    <i class="fas fa-location-dot"></i>
                    ${event.location}
                </div>
            </div>
            <div class="card-footer">
                <div class="price-section">
                    <span class="price-label">Starting from</span>
                    <div class="price-value">$${event.price}</div>
                </div>
                ${loggedIn ? `<a href="event-details.html?id=${event.id}" class="btn-book">Book Now</a>` : `<a href="signin.html" class="btn-book">Book Now</a>`}
            </div>
        </div>
    `).join("");
}

/* --- Category Filter --- */
function setCategory(category) {
    // Redirect to events page with category filters like events.html
    if (!category || category === 'All') {
        window.location.href = 'events.html';
        return;
    }

    const params = new URLSearchParams();
    params.set('categories', category.toLowerCase());
    window.location.href = `events.html?${params.toString()}`;
}

/* --- Search Events (UPDATED TO REDIRECT) --- */
function filterEvents() {
    const searchInput = document.getElementById("searchInput").value.trim();
    const locationSelect = document.querySelector('.location-select');
    const selectedCity = locationSelect ? (locationSelect.value || locationSelect.options?.[locationSelect.selectedIndex]?.text || '') : '';
    
    // If neither search nor specific city chosen, prompt the user
    const hasCityFilter = selectedCity && selectedCity !== 'All';
    const hasSearch = searchInput !== '';
    if (!hasSearch && !hasCityFilter) {
        if (typeof showNotification === 'function') {
            showNotification("Select a city or enter a search");
        }
        return;
    }

    // Redirect to events page with applicable query params
    const params = new URLSearchParams();
    if (hasSearch) params.set('search', searchInput);
    if (hasCityFilter) params.set('city', selectedCity);
    window.location.href = `events.html?${params.toString()}`;
}

/* --- Reset Filters --- */
function resetFilters() {
    currentCategory = "All";
    currentSearch = "";
    document.getElementById("searchInput").value = "";
    renderEvents();
    
    document.querySelectorAll(".category-btn").forEach(btn => {
        btn.classList.remove("active");
    });
    document.querySelectorAll(".category-btn")[0].classList.add("active");
}

/* --- Modal Management --- */
function openModal(eventId) {
    selectedEvent = events.find(e => e.id === eventId);
    if (!selectedEvent) return;
    
    document.getElementById("modalEventTitle").textContent = selectedEvent.title;
    document.getElementById("modalEventDetails").innerHTML = `
        <span><i class="fas fa-calendar"></i> ${selectedEvent.date}</span>
        <span class="highlight">${selectedEvent.price > 100 ? "Premium" : "Standard"}</span>
    `;
    document.getElementById("ticketCount").value = 1;
    updateTotal();
    
    document.body.style.overflow = "hidden";
    document.getElementById("bookingModal").classList.add("active");
}

function closeModal() {
    document.getElementById("bookingModal").classList.remove("active");
    document.body.style.overflow = "";
    selectedEvent = null;
}

/* --- Ticket Management --- */
function adjustTickets(change) {
    const input = document.getElementById("ticketCount");
    let value = parseInt(input.value) || 1;
    value += change;
    
    if (value < 1) value = 1;
    if (value > 10) value = 10;
    
    input.value = value;
    updateTotal();
}

function updateTotal() {
    if (!selectedEvent) return;
    
    const ticketCount = parseInt(document.getElementById("ticketCount").value) || 1;
    const total = ticketCount * selectedEvent.price;
    document.getElementById("totalPrice").textContent = `$${total}`;
}

/* --- Booking Submission --- */
function handleBooking(event) {
    event.preventDefault();
    
    if (!selectedEvent) return;
    
    const name = document.getElementById("visitorName").value;
    const email = document.getElementById("visitorEmail").value;
    const tickets = document.getElementById("ticketCount").value;
    
    if (!name || !email || ! tickets) {
        if (typeof showNotification === 'function') {
            showNotification("Please fill all fields");
        }
        return;
    }
    
    if (!email.includes("@")) {
        if (typeof showNotification === 'function') {
            showNotification("Please enter a valid email");
        }
        return;
    }
    
    if (tickets < 1 || tickets > 10) {
        if (typeof showNotification === 'function') {
            showNotification("Tickets must be between 1 and 10");
        }
        return;
    }
    
    closeModal();
    showNotification(`Successfully booked ${tickets} ticket(s) for "${selectedEvent.title}"!`);
    
    document.querySelector("form").reset();
    renderEvents();
}

/* --- Notification --- */
function showNotification(message) {
    const notification = document.getElementById("notification");
    if (! notification) return;
    
    notification.textContent = message;
    notification.classList.add("show");
    
    setTimeout(() => {
        notification.classList.remove("show");
    }, 3000);
}