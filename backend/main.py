from app.api.auth import router as auth_router
from app.api.events import router as events_router
from app.api.health import router as health_router
from app.api.my_events import router as my_events_router
from app.core import config
from app.db.session import init_db
from fastapi import FastAPI
from fastapi_pagination import add_pagination

app = FastAPI()
add_pagination(app)

routers = [auth_router, events_router, my_events_router]
for router in routers:
    app.include_router(router, prefix=config.API_V1_PREFIX)

app.include_router(health_router)


@app.on_event("startup")
def on_startup():
    init_db()
