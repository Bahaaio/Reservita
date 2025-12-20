/**
 * API Service - Handles all backend API calls
 * Base URL: http://127.0.0.1:8000
 */

const API_BASE_URL = "https://reservita.leapcell.app";

// ================================
// HELPER FUNCTIONS
// ================================

function getAuthToken() {
  return localStorage.getItem("access_token");
}

function setAuthToken(token, expiresIn) {
  localStorage.setItem("access_token", token);
  const expiryTime = new Date().getTime() + expiresIn * 1000;
  localStorage.setItem("token_expiry", expiryTime);
}

function clearAuthToken() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("token_expiry");
}

function isTokenExpired() {
  const expiry = localStorage.getItem("token_expiry");
  if (!expiry) return true;
  return new Date().getTime() > parseInt(expiry);
}

async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getAuthToken();

  const headers = {
    ...options.headers,
  };

  // Add Authorization header if token exists and not expired
  if (token && !isTokenExpired()) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Add Content-Type for JSON requests (only if not already set)
  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !headers["Content-Type"]
  ) {
    headers["Content-Type"] = "application/json";
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);

    // Handle 401 Unauthorized
    if (response.status === 401) {
      clearAuthToken();
      if (!window.location.pathname.includes("signin.html")) {
        window.location.href = "signin.html";
      }
      throw new Error("Unauthorized - please login again");
    }

    // Handle other error responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      // Handle validation errors (422)
      if (response.status === 422 && errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          const errors = errorData.detail
            .map((err) => `${err.loc?.join(".")}: ${err.msg}`)
            .join(", ");
          throw new Error(errors);
        }
      }

      const errorMessage =
        errorData.detail ||
        errorData.message ||
        `HTTP error! status: ${response.status}`;
      throw new Error(errorMessage);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return null;
    }

    // Parse JSON response
    return await response.json();
  } catch (error) {
    // Handle network errors
    if (error.name === "TypeError" && error.message.includes("fetch")) {
      console.error("Network error - is the backend running?");
      throw new Error(
        "Cannot connect to server. Please ensure the backend is running at " +
          API_BASE_URL,
      );
    }
    console.error("API Request Error:", error);
    throw error;
  }
}

// ================================
// AUTHENTICATION API
// ================================

const AuthAPI = {
  async register(fullName, email, password, phoneNumber, isAgency) {
    const response = await apiRequest("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify({
        full_name: fullName,
        email: email,
        password: password,
        phone_number: phoneNumber,
        is_agency: isAgency,
      }),
    });

    // Store token from registration response
    if (response.token) {
      setAuthToken(response.token.access_token, response.token.expires_in);
    }

    return response;
  },

  async login(email, password) {
    // OAuth2 requires form-urlencoded data
    const formData = new URLSearchParams();
    formData.append("username", email); // Backend uses 'username' field for email
    formData.append("password", password);

    console.log("Login request:", { email, body: formData.toString() });

    const response = await apiRequest("/api/v1/auth/token", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData.toString(), // Ensure it's a string
    });

    // Store token
    setAuthToken(response.access_token, response.expires_in);

    return response;
  },

  logout() {
    clearAuthToken();
    localStorage.removeItem("currentUser");
  },
};

// ================================
// PROFILE API
// ================================

const ProfileAPI = {
  async getProfile() {
    return await apiRequest("/api/v1/users/me", {
      method: "GET",
    });
  },

  async updateProfile(fullName, phoneNumber) {
    const body = {};
    if (fullName !== null) body.full_name = fullName;
    if (phoneNumber !== null) body.phone_number = phoneNumber;

    return await apiRequest("/api/v1/users/me", {
      method: "PATCH",
      body: JSON.stringify(body),
    });
  },

  async getAvatar() {
    // Returns image data
    const token = getAuthToken();
    const response = await fetch(`${API_BASE_URL}/api/v1/users/me/avatar`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      return await response.blob();
    }
    return null;
  },

  async uploadAvatar(file) {
    const formData = new FormData();
    formData.append("file", file);

    const token = getAuthToken();
    const response = await fetch(`${API_BASE_URL}/api/v1/users/me/avatar`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to upload avatar");
    }
  },

  async deleteAvatar() {
    return await apiRequest("/api/v1/users/me/avatar", {
      method: "DELETE",
    });
  },
};

// ================================
// EVENTS API
// ================================

const EventsAPI = {
  async listAllEvents(page = 1, size = 50) {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    });
    return await apiRequest(`/api/v1/events?${params}`, {
      method: "GET",
    });
  },

  async getEvent(eventId) {
    return await apiRequest(`/api/v1/events/${eventId}`, {
      method: "GET",
    });
  },

  async getEventSeats(eventId) {
    return await apiRequest(`/api/v1/events/${eventId}/seats`, {
      method: "GET",
    });
  },

  async getBanner(bannerId) {
    const token = getAuthToken();
    const response = await fetch(
      `${API_BASE_URL}/api/v1/events/banners/${bannerId}`,
      {
        headers: token
          ? {
              Authorization: `Bearer ${token}`,
            }
          : {},
      },
    );

    if (response.ok) {
      return await response.blob();
    }
    return null;
  },
};

// ================================
// AGENCY EVENTS API
// ================================

const AgencyEventsAPI = {
  async listMyEvents(page = 1, size = 50) {
    const safeSize = Math.min(Math.max(parseInt(size, 10) || 50, 1), 100);
    const safePage = Math.max(parseInt(page, 10) || 1, 1);
    const params = new URLSearchParams({
      page: safePage.toString(),
      size: safeSize.toString(),
    });
    return await apiRequest(`/api/v1/my-events?${params}`, {
      method: "GET",
    });
  },

  async getAnalytics() {
    return await apiRequest("/api/v1/my-events/analytics", {
      method: "GET",
    });
  },

  async listEventsAnalytics() {
    return await apiRequest("/api/v1/my-events/analytics/events", {
      method: "GET",
    });
  },

  async createEvent(eventData) {
    return await apiRequest("/api/v1/my-events", {
      method: "POST",
      body: JSON.stringify({
        title: eventData.title,
        description: eventData.description,
        category: eventData.category,
        city: eventData.city,
        venue: eventData.venue,
        address: eventData.address,
        starts_at: eventData.starts_at,
        ends_at: eventData.ends_at,
        ticket_price: eventData.ticket_price,
        vip_ticket_price: eventData.vip_ticket_price,
        total_seats: eventData.total_seats || 100,
        vip_seats_count: eventData.vip_seats_count || 10,
      }),
    });
  },

  async updateEvent(eventId, eventData) {
    return await apiRequest(`/api/v1/my-events/${eventId}`, {
      method: "PUT",
      body: JSON.stringify({
        title: eventData.title,
        description: eventData.description,
        category: eventData.category,
        city: eventData.city,
        venue: eventData.venue,
        address: eventData.address,
        starts_at: eventData.starts_at,
        ends_at: eventData.ends_at,
        ticket_price: eventData.ticket_price,
        vip_ticket_price: eventData.vip_ticket_price,
        total_seats: eventData.total_seats || 100,
        vip_seats_count: eventData.vip_seats_count || 10,
      }),
    });
  },

  async uploadBanner(eventId, file) {
    const formData = new FormData();
    formData.append("file", file);

    const token = getAuthToken();
    const response = await fetch(
      `${API_BASE_URL}/api/v1/my-events/${eventId}/banners`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      },
    );

    if (!response.ok) {
      throw new Error("Failed to upload banner");
    }

    return await response.json();
  },

  async deleteBanner(eventId, bannerId) {
    return await apiRequest(
      `/api/v1/my-events/${eventId}/banners/${bannerId}`,
      {
        method: "DELETE",
      },
    );
  },

  async deleteEvent(eventId) {
    return await apiRequest(`/api/v1/my-events/${eventId}`, {
      method: "DELETE",
    });
  },
};

// ================================
// TICKETS API
// ================================

const TicketsAPI = {
  async listMyTickets() {
    return await apiRequest("/api/v1/tickets", {
      method: "GET",
    });
  },

  async bookTicket(eventId, seatNumber) {
    return await apiRequest("/api/v1/tickets", {
      method: "POST",
      body: JSON.stringify({
        event_id: parseInt(eventId),
        seat_number: parseInt(seatNumber),
      }),
    });
  },

  async getTicket(ticketId) {
    return await apiRequest(`/api/v1/tickets/${ticketId}`, {
      method: "GET",
    });
  },

  async cancelTicket(ticketId) {
    return await apiRequest(`/api/v1/tickets/${ticketId}`, {
      method: "DELETE",
    });
  },

  async getTicketQR(ticketId) {
    const token = getAuthToken();
    const response = await fetch(
      `${API_BASE_URL}/api/v1/tickets/${ticketId}/qr`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    if (response.ok) {
      return await response.blob();
    }
    return null;
  },

  async verifyQR(token) {
    return await apiRequest("/api/v1/tickets/qr/verify", {
      method: "POST",
      body: JSON.stringify({ qr_token: token }),
    });
  },
};

// ================================
// REVIEWS API
// ================================

const ReviewsAPI = {
  async createReview(ticketId, rating, comment = null) {
    const body = { rating };
    if (comment) body.comment = comment;

    return await apiRequest(`/api/v1/tickets/${ticketId}/review`, {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  async getReview(reviewId) {
    return await apiRequest(`/api/v1/reviews/${reviewId}`, {
      method: "GET",
    });
  },

  async updateReview(reviewId, rating = null, comment = null) {
    const body = {};
    if (rating !== null) body.rating = rating;
    if (comment !== null) body.comment = comment;

    return await apiRequest(`/api/v1/reviews/${reviewId}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    });
  },

  async deleteReview(reviewId) {
    return await apiRequest(`/api/v1/reviews/${reviewId}`, {
      method: "DELETE",
    });
  },

  async listEventReviews(eventId, page = 1, size = 50) {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    });
    return await apiRequest(`/api/v1/events/${eventId}/reviews?${params}`, {
      method: "GET",
    });
  },
};

// ================================
// FAVORITES API
// ================================

const FavoritesAPI = {
  async getFavorites() {
    return await apiRequest("/api/v1/users/me/favorites", {
      method: "GET",
    });
  },

  async addFavorite(eventId) {
    return await apiRequest(`/api/v1/users/me/favorites/`, {
      method: "POST",
      body: JSON.stringify({ event_id: eventId }),
    });
  },

  async removeFavorite(eventId) {
    return await apiRequest(`/api/v1/users/me/favorites/${eventId}`, {
      method: "DELETE",
    });
  },

  async clearAllFavorites() {
    return await apiRequest("/api/v1/users/me/favorites", {
      method: "DELETE",
    });
  },
};

// ================================
// HEALTH API
// ================================

const HealthAPI = {
  async checkHealth() {
    return await apiRequest("/health", {
      method: "GET",
    });
  },
};
