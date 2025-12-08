from fastapi import FastAPI

from app.api.health import router as health_router
from app.db.session import init_db

app = FastAPI()

routers = []
for router in routers:
    app.include_router(router, prefix="/api/v1")

app.include_router(health_router)


@app.on_event("startup")
def on_startup():
    init_db()
