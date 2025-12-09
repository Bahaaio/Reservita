from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.core import config
from app.db.session import init_db
from fastapi import FastAPI

app = FastAPI()

routers = [auth_router]
for router in routers:
    app.include_router(router, prefix=config.API_V1_PREFIX)

app.include_router(health_router)


@app.on_event("startup")
def on_startup():
    init_db()
