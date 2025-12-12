# Ticket Reservation System - Backend

FastAPI-based REST API for event management and ticket reservations.

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLite with SQLModel
- **Authentication:** JWT (PyJWT + Argon2)
- **Server:** Uvicorn

## Quick Start

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Interactive API documentation with Swagger UI:

- **Swagger UI:** <http://localhost:8000/docs>
- **ReDoc:** <http://localhost:8000/redoc>

## Configuration

Settings are managed using Pydantic Settings in [config.py](./app/core/config.py)

| Setting                       | Default            | Description           |
| ----------------------------- | ------------------ | --------------------- |
| `DATABASE_URL`                | `sqlite:///app.db` | Database connection   |
| `API_V1_STR`                  | `/api/v1`          | API version prefix    |
| `JWT_SECRET_KEY`              | Auto-generated     | JWT signing key       |
| `JWT_ALGORITHM`               | `HS256`            | JWT algorithm         |
| `ACCESS_TOKEN_EXPIRE_SECONDS` | `3600` (1 hour)    | Token expiration      |
| `MAX_AVATAR_SIZE_MB`          | `5`                | Max avatar size       |
| `MAX_BANNER_SIZE_MB`          | `10`               | Max banner size       |
| `MAX_BANNERS_PER_EVENT`       | `5`                | Max banners per event |

> All settings can be overridden using environment variables.

## Database Schema

![schema](/docs/backend/schema.svg)

## Project Structure

```
backend/
├── app/
│   ├── api/          # API route handlers (auth, events, my_events)
│   ├── core/         # Configuration and security utilities
│   ├── db/           # Database models and session management
│   ├── dto/          # Request/response schemas (Pydantic)
│   ├── services/     # Business logic layer
│   ├── exceptions/   # Custom exceptions
│   └── util/         # Utility functions (file handling, etc.)
├── uploads/          # File uploads (avatars, banners)
├── main.py           # Application entry point
└── requirements.txt  # Dependencies
```

## Development

### Code Organization

- **API Layer:** Route definitions and request handling
- **Service Layer:** Business logic and database operations
- **DTO Layer:** Request/response validation with Pydantic
- **Database Layer:** SQLModel definitions

### Authentication

Protected endpoints require a Bearer token. Use the "Authorize" button in Swagger UI:

1. Register or login to get a token
2. Click "Authorize" button
3. Use email in the "username" field
4. Enter password
