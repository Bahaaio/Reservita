# Reservita

A full-stack event ticketing and reservation platform built with FastAPI and vanilla JavaScript.

## Overview

Reservita is a ticket reservation system that allows agencies to create and manage events, users to browse and book tickets, and provides features like seat selection, QR code tickets, reviews, and favorites.

## Gallery

See **[gallery.md](gallery.md)** for visual documentation of all pages and features.

## Tech Stack

### Backend

- **Framework:** FastAPI
- **Database:** SQLite with SQLModel/SQLAlchemy
- **Authentication:** JWT with Argon2 password hashing
- **Email:** SMTP with HTML templates
- **Server:** Uvicorn (ASGI)

### Frontend

- **Framework:** Vanilla JavaScript (ES6+)
- **Styling:** Custom CSS
- **API Communication:** Fetch API
- **QR Scanner:** Camera API integration

## Features

### User Features

- Browse events with advanced filtering (category, city, price, date)
- Purchase tickets with seat selection (regular/VIP)
- QR code ticket generation
- Add events to favorites
- Write reviews for attended events
- User dashboard with ticket history
- Profile management with avatar upload

### Agency Features

- Create and manage events
- Upload event banners (up to 5 per event)
- Configure dynamic seat capacity (VIP and regular)
- View analytics (tickets sold, revenue)
- Delete events with cascading cleanup
- QR code ticket verification

### System Features

- JWT-based authentication
- Email notifications (registration, ticket confirmation, cancellation)
- Pagination for all list endpoints
- Image upload validation
- Secure password hashing with Argon2

## Getting Started

### Backend Setup

1. Navigate to backend directory:

```bash
cd backend
```

2. Create virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run the server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

> check [backend/README.md](backend/README.md) for more details on configuration and environment variables.

### Frontend Setup

1. Navigate to frontend directory:

```bash
cd frontend
```

2. Serve with python's HTTP server:

```bash
python -m http.server 8080
```

The frontend will be available at `http://127.0.0.1:8080`

## API Documentation

Interactive API documentation is available when the backend is running:

- **Swagger UI:** <http://localhost:8000/docs>
- **ReDoc:** <http://localhost:8000/redoc>

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token

### Events (Public)

- `GET /api/v1/events` - List events with filters
- `GET /api/v1/events/{id}` - Get event details

### My Events (Agency)

- `GET /api/v1/my-events` - List agency events
- `POST /api/v1/my-events` - Create event
- `PATCH /api/v1/my-events/{id}` - Update event
- `DELETE /api/v1/my-events/{id}` - Delete event
- `POST /api/v1/my-events/{id}/banners` - Upload banner
- `DELETE /api/v1/my-events/{id}/banners/{banner_id}` - Delete banner
- `GET /api/v1/my-events/analytics` - Agency analytics
- `GET /api/v1/my-events/analytics/events` - Per-event analytics

### Tickets

- `GET /api/v1/tickets/me` - List user tickets
- `POST /api/v1/tickets` - Book ticket
- `DELETE /api/v1/tickets/{id}` - Cancel ticket
- `GET /api/v1/tickets/{id}/qr` - Download QR code
- `POST /api/v1/tickets/qr/verify` - Verify QR code (agency)

### Reviews

- `GET /api/v1/reviews` - List event reviews
- `POST /api/v1/reviews` - Write review
- `PATCH /api/v1/reviews/{id}` - Update review
- `DELETE /api/v1/reviews/{id}` - Delete review

### Favorites

- `GET /api/v1/users/me/favorites` - List favorites
- `POST /api/v1/users/me/favorites` - Add favorite
- `DELETE /api/v1/users/me/favorites/{event_id}` - Remove favorite
- `DELETE /api/v1/users/me/favorites` - Clear all favorites

### Users

- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update profile
- `POST /api/v1/users/me/avatar` - Upload avatar
- `GET /api/v1/users/{id}/avatar` - Download avatar

## Development

### Architecture

The backend follows a layered architecture:

1. **API Layer:** Route handlers validate input and return responses
2. **Service Layer:** Contains business logic and database operations
3. **DTO Layer:** Pydantic models for request/response validation
4. **Database Layer:** SQLModel definitions and relationships
