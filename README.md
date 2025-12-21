# Reservita

A full-stack event ticketing platform with intelligent seat selection, QR code verification, and real-time analytics.

[![Live Demo](https://img.shields.io/badge/demo-live-success.svg)](https://bahaaio.github.io/ticket-reservation)
[![API Docs](https://img.shields.io/badge/API-docs-orange.svg)](https://reservita.leapcell.app/docs)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ Features

### User Features

- Browse events with advanced filtering (category, city, price, date)
- Purchase tickets with seat selection (regular/VIP)
- Digital QR code tickets
- Add events to favorites
- Rate and review attended events
- User dashboard with ticket history
- Profile management with avatar upload

### Agency Features

- Create and manage events
- Upload event banners (up to 5 per event)
- Configure seat capacity (VIP and regular tiers)
- Real-time analytics (sales, revenue, attendance)
- QR code ticket verification
- Delete events

### System Features

- JWT-based authentication
- Email notifications (registration, ticket confirmation, cancellation)
- Pagination for all list endpoints
- Image upload validation
- Secure password hashing with Argon2

## 🖼️ Gallery

See the full visual documentation in **[gallery.md](gallery.md)** showcasing all pages and features.

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Bahaaio/reservita.git
cd reservita
```

### 2. Start the Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

The API will be running at `http://localhost:8000`

> See [backend/README.md](backend/README.md) for configuration options and API documentation.

### 3. Start the Frontend

```bash
cd frontend

# Serve with Python's built-in server
python -m http.server 8080
```

Visit `http://127.0.0.1:8080` in your browser.

## 🏗️ Tech Stack

### Backend

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[SQLModel](https://sqlmodel.tiangolo.com/)** - SQL database with Python type hints
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation using Python annotations
- **[Uvicorn](https://www.uvicorn.org/)** - Lightning-fast ASGI server
- **[PyJWT](https://pyjwt.readthedocs.io/)** - JSON Web Token implementation
- **[Argon2](https://github.com/hynek/argon2-cffi)** - Secure password hashing

### Frontend

- **Vanilla JavaScript** - No frameworks, pure ES6+ for maximum performance
- **Custom CSS** - Responsive design with modern styling
- **Fetch API** - Native HTTP client for API communication
- **Camera API** - Built-in QR code scanning capabilities

### Database

- **SQLite** - Local development
- **PostgreSQL** - Production deployment (Aiven Cloud)

### Deployment

- **GitHub Pages** - Static frontend hosting
- **Leapcell** - Backend API hosting

## 📧 Email Templates

Reservita sends beautifully designed HTML emails for:

- ✉️ Welcome message (registration)
- 🎫 Ticket confirmation (booking)
- ❌ Ticket cancellation
- ⭐ Review request (after event ends)

Templates are located in `backend/app/templates/emails/`

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
