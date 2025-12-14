from app.api.auth import router as auth_router
from app.api.events import router as events_router
from app.api.health import router as health_router
from app.api.my_events import router as my_events_router
from app.api.reviews import router as reviews_router
from app.api.tickets import router as tickets_router
from app.core.config import settings
from app.db.session import init_db
from fastapi import FastAPI
from fastapi_pagination import add_pagination

app = FastAPI(title="Ticket Reservation API")
add_pagination(app)

routers = [auth_router, events_router, my_events_router, reviews_router, tickets_router]
for router in routers:
    app.include_router(router, prefix=settings.API_V1_STR)

app.include_router(health_router)


@app.on_event("startup")
def on_startup():
    init_db()
