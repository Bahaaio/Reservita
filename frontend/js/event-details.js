// ================================
// GET EVENT FROM URL
// ================================

function getEventIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id');
}

async function getEventById(id) {
    try {
        const backendEvent = await EventsAPI.getEvent(id);
        
        // Format the event data
        const startsAt = new Date(backendEvent.starts_at);
        const endsAt = new Date(backendEvent.ends_at);
        
        const startTime = startsAt.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        const endTime = endsAt.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        
        return {
            id: backendEvent.id,
            title: backendEvent.title,
            city: backendEvent.city,
            category: backendEvent.category.charAt(0).toUpperCase() + backendEvent.category.slice(1),
            price: backendEvent.ticket_price,
            vipPrice: backendEvent.vip_ticket_price,
            dateString: backendEvent.starts_at,
            time: `${startTime} - ${endTime}`,
            image: backendEvent.banner_ids && backendEvent.banner_ids.length > 0 ? `${API_BASE_URL}/api/v1/events/banners/${backendEvent.banner_ids[0]}` : 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600',
            venue: backendEvent.venue,
            venueAddress: backendEvent.address,
            description: backendEvent.description,
            longDescription: backendEvent.description,
            galleryImages: backendEvent.banner_ids && backendEvent.banner_ids.length > 0 ? backendEvent.banner_ids.map(id => `${API_BASE_URL}/api/v1/events/banners/${id}`) : ['https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600'],
            averageRating: backendEvent.average_rating || 0,
            isFavorited: backendEvent.is_favorited || false,
            seatsLeft: 0, // Will be updated from seats API
            totalSeats: 0 // Will be updated from seats API
        };
    } catch (error) {
        console.error('Failed to fetch event:', error);
        return null;
    }
}

async function getEventSeats(eventId) {
    try {
        const seatsData = await EventsAPI.getEventSeats(eventId);
        return seatsData;
    } catch (error) {
        console.error('Failed to fetch event seats:', error);
        return null;
    }
}

// ================================
// RENDER EVENT DETAILS
// ================================

async function renderEventDetails() {
    const eventId = getEventIdFromURL();
    console.log('Event ID from URL:', eventId);
    
    if (!eventId) {
        console.error('No event ID in URL');
        window.location.href = 'events.html';
        return;
    }
    
    // Show loading state
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        heroSection.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; min-height: 400px; color: white;"><i class="fa-solid fa-spinner fa-spin" style="font-size: 3rem;"></i></div>';
    }
    
    const event = await getEventById(eventId);
    console.log('Found event:', event);
    
    if (!event) {
        console.error('Event not found');
        document.body.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; color: white;">
                <h1 style="font-size: 3rem; margin-bottom: 20px;">Event Not Found</h1>
                <p style="color: var(--text-muted); margin-bottom: 30px;">The event you're looking for doesn't exist.</p>
                <a href="events.html" style="background: var(--brand-dark); color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none;">Back to Events</a>
            </div>
        `;
        return;
    }
    
    // Set global currentEvent for seat modal functions
    window.currentEvent = event;
    
    // Fetch seats information
    const seatsData = await getEventSeats(eventId);
    if (seatsData) {
        event.totalSeats = seatsData.summary.total_seats;
        event.seatsLeft = seatsData.summary.available_seats;
    }
    
    // Update page title
    document.title = `${event.title} | Resrvetia`;
    
    // Format date from ISO string
    const eventDate = new Date(event.dateString);
    const dateStr = eventDate.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
    });
    
    const priceDisplay = event.price === 0 ? 'Free' : `Starting at $${event.price}`;
    
    // Calculate seats percentage (avoid division by zero)
    const seatsPercentage = event.totalSeats > 0 ? ((event.totalSeats - event.seatsLeft) / event.totalSeats) * 100 : 0;
    
    // Update Hero Section (reuse existing heroSection variable)
    const heroSectionEl = document.querySelector('.hero-section');
    if (heroSectionEl) {
        heroSectionEl.style.backgroundImage = `url('${event.galleryImages[0]}')`;
        console.log('Set hero image to:', event.galleryImages[0]);
        
        // Test if image loads
        const testImg = new Image();
        testImg.onload = () => console.log('✓ Hero image loaded successfully');
        testImg.onerror = () => {
            console.error('✗ Hero image failed to load:', event.galleryImages[0]);
            // Fallback to placeholder
            heroSectionEl.style.backgroundImage = `url('https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=1200')`;
        };
        testImg.src = event.galleryImages[0];
    }
    
    const eventBadge = document.querySelector('.event-badge');
    const heroTitle = document.querySelector('.hero-title');
    
    if (eventBadge) eventBadge.textContent = event.category;
    if (heroTitle) heroTitle.textContent = event.title;
    
    const heroMetaHTML = `
        <div class="meta-item">
            <i class="fa-regular fa-calendar"></i> ${dateStr} • ${event.time}
        </div>
        <div class="meta-item">
            <i class="fa-solid fa-location-dot"></i> ${event.venue}, ${event.city}
        </div>
    `;
    const heroMeta = document.querySelector('.hero-meta');
    if (heroMeta) heroMeta.innerHTML = heroMetaHTML;
    
    // Update Description
    const descriptionParagraphs = event.longDescription.split('\n\n');
    const descriptionHTML = descriptionParagraphs.map(p => `<p>${p}</p>`).join('<br>');
    const descriptionText = document.querySelector('.description-text');
    if (descriptionText) {
        descriptionText.innerHTML = descriptionHTML;
        console.log('Set description');
    }
    
    // Update Gallery
    const galleryHTML = event.galleryImages.map((img, index) => `
        <div class="gallery-item">
            <img src="${img}" class="gallery-img" alt="Gallery ${index + 1}" onerror="this.src='https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600'">
        </div>
    `).join('');
    const galleryGrid = document.querySelector('.gallery-grid');
    if (galleryGrid) {
        galleryGrid.innerHTML = galleryHTML;
        console.log('Set gallery with', event.galleryImages.length, 'images');
    }
    
    // Update Venue
    const venueH3 = document.querySelector('.venue-box h3');
    const venueP = document.querySelector('.venue-box p');
    if (venueH3) venueH3.textContent = event.venue;
    if (venueP) venueP.textContent = event.venueAddress;
    
    // Update Booking Card
    const displayPrice = document.getElementById('displayPrice');
    const totalDisplay = document.getElementById('totalDisplay');
    if (displayPrice) displayPrice.textContent = priceDisplay;
    if (totalDisplay) totalDisplay.textContent = priceDisplay;
    
    // Update seats indicator
    const seatsText = event.seatsLeft < 20 ? 
        `Hurry! Almost sold out` : 
        `Limited seats available`;
    
    const seatsTextElement = document.querySelector('.seats-text');
    if (seatsTextElement) {
        seatsTextElement.innerHTML = `
            <span>${seatsText}</span>
            <span>${event.seatsLeft} seats left</span>
        `;
    }
    
    const seatsBarFill = document.querySelector('.seats-bar-fill');
    if (seatsBarFill) seatsBarFill.style.width = `${seatsPercentage}%`;
    
    // Set up quantity controls
    setupQuantityControls(event);
    
    // Note: Book button uses openSeatModal() from event-details.html inline script
    // No need to override it here
    
    console.log('Event details rendered successfully');
    
    // Dispatch event to notify that event is loaded
    window.dispatchEvent(new Event('eventLoaded'));
    
    // Also call loadTopReviews directly if it exists
    if (typeof loadTopReviews === 'function') {
        loadTopReviews();
    }
}

// ================================
// QUANTITY CONTROLS
// ================================

let currentQuantity = 1;

function setupQuantityControls(event) {
    let qtyDisplay = document.getElementById('qtyDisplay');
    
    if (!qtyDisplay) {
        // Create quantity controls if they don't exist
        const qtyControlHTML = `
            <div class="qty-control">
                <span style="color: var(--text-muted); font-weight: 600;">Quantity</span>
                <div style="display: flex; gap: 15px; align-items: center;">
                    <button class="qty-btn" id="qtyMinus">
                        <i class="fa-solid fa-minus"></i>
                    </button>
                    <input type="number" id="qtyDisplay" class="qty-input" value="1" min="1" max="${event.seatsLeft}" readonly>
                    <button class="qty-btn" id="qtyPlus">
                        <i class="fa-solid fa-plus"></i>
                    </button>
                </div>
            </div>
        `;
        
        const bookingCard = document.querySelector('.booking-card');
        const seatsIndicator = bookingCard.querySelector('.seats-indicator');
        if (seatsIndicator) {
            seatsIndicator.insertAdjacentHTML('afterend', qtyControlHTML);
        }
    }
    
    const qtyMinusBtnElement = document.getElementById('qtyMinus');
    const qtyPlusBtnElement = document.getElementById('qtyPlus');
    
    if (qtyMinusBtnElement && qtyPlusBtnElement) {
        // Remove existing listeners by cloning elements
        const newMinusBtn = qtyMinusBtnElement.cloneNode(true);
        const newPlusBtn = qtyPlusBtnElement.cloneNode(true);
        qtyMinusBtnElement.parentNode.replaceChild(newMinusBtn, qtyMinusBtnElement);
        qtyPlusBtnElement.parentNode.replaceChild(newPlusBtn, qtyPlusBtnElement);
        
        newMinusBtn.addEventListener('click', () => {
            if (currentQuantity > 1) {
                currentQuantity--;
                updateQuantityDisplay(event);
            }
        });
        
        newPlusBtn.addEventListener('click', () => {
            if (currentQuantity < event.seatsLeft) {
                currentQuantity++;
                updateQuantityDisplay(event);
            }
        });
    }
}

function updateQuantityDisplay(event) {
    document.getElementById('qtyDisplay').value = currentQuantity;
    const total = event.price * currentQuantity;
    document.getElementById('totalDisplay').textContent = `$${total}`;
}

function updatePricingDisplay(event, seatsData) {
    if (!seatsData || !seatsData.pricing) return;
    
    const displayPrice = document.getElementById('displayPrice');
    const totalDisplay = document.getElementById('totalDisplay');
    
    // Show both pricing options if VIP seats exist
    const hasVipSeats = seatsData.seats.some(seat => seat.seat_type === 'vip');
    const hasRegularSeats = seatsData.seats.some(seat => seat.seat_type === 'regular');
    
    let priceText = '';
    if (hasRegularSeats && hasVipSeats) {
        priceText = `Regular: $${seatsData.pricing.regular} | VIP: $${seatsData.pricing.vip}`;
    } else if (hasVipSeats) {
        priceText = `$${seatsData.pricing.vip}`;
    } else {
        priceText = `$${seatsData.pricing.regular}`;
    }
    
    if (displayPrice) displayPrice.textContent = priceText;
    if (totalDisplay) totalDisplay.textContent = `$${seatsData.pricing.regular}`;
}

// ================================
// BOOK BUTTON
// ================================

let selectedSeatNumber = null;
let selectedSeatType = null;
let seatsDataGlobal = null;

async function setupBookButton(event) {
    const bookBtn = document.querySelector('.btn-book');
    
    if (!bookBtn) {
        console.error('Book button not found');
        return;
    }
    
    // Fetch available seats
    seatsDataGlobal = await getEventSeats(event.id);
    
    if (!seatsDataGlobal || !seatsDataGlobal.seats || seatsDataGlobal.seats.length === 0) {
        console.error('No seats found for this event');
        if (typeof showNotification === 'function') {
            showNotification('No seats available for this event');
        }
        return;
    }
    
    // Update pricing display with both regular and VIP prices
    updatePricingDisplay(event, seatsDataGlobal);
    
    // Clone button to remove existing event listeners
    const newBookBtn = bookBtn.cloneNode(true);
    bookBtn.parentNode.replaceChild(newBookBtn, bookBtn);
    
    newBookBtn.addEventListener('click', async () => {
        const currentUser = JSON.parse(localStorage.getItem('currentUser'));
        
        if (!currentUser) {
            // Redirect to sign in
            window.location.href = 'signin.html?redirect=event-details.html?id=' + event.id;
            return;
        }
        
        // Find first available seat if not selected
        if (!selectedSeatNumber && seatsDataGlobal) {
            const availableSeat = seatsDataGlobal.seats.find(seat => seat.is_available);
            if (availableSeat) {
                selectedSeatNumber = availableSeat.seat_number;
                selectedSeatType = availableSeat.seat_type;
            } else {
                if (typeof showNotification === 'function') {
                    showNotification('No seats available');
                }
                return;
            }
        }
        
        // Show loading on button
        const originalText = newBookBtn.innerHTML;
        newBookBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Booking...';
        newBookBtn.disabled = true;
        
        try {
            // Book ticket via API
            const ticket = await TicketsAPI.bookTicket(event.id, selectedSeatNumber);
            
            // Show success and redirect to payment
            newBookBtn.innerHTML = '<i class="fa-solid fa-check"></i> Success!';
            newBookBtn.style.backgroundColor = '#10b981';
            
            setTimeout(() => {
                const eventTitle = encodeURIComponent(event.title);
                const ticketId = ticket.id;
                const total = ticket.price_paid;
                
                // Always pass ticket ID in the "tickets" param so payment.html
                // can load full details and QR from the backend.
                window.location.href = `payment.html?tickets=${ticketId}&event=${eventTitle}&total=${total}`;
            }, 1000);
            
        } catch (error) {
            console.error('Booking failed:', error);
            
            // Show error
            newBookBtn.innerHTML = '<i class="fa-solid fa-exclamation-circle"></i> Error';
            newBookBtn.style.backgroundColor = '#ef4444';
            
            if (typeof showNotification === 'function') {
                showNotification(error.message || 'Failed to book ticket. Please try again.');
            }
            
            // Reset button
            setTimeout(() => {
                newBookBtn.innerHTML = originalText;
                newBookBtn.style.backgroundColor = '';
                newBookBtn.disabled = false;
            }, 2000);
        }
    });
}

// ================================
// INITIALIZATION
// ================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, rendering event details...');
    renderEventDetails();
});