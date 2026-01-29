from fastapi import APIRouter

from app.api.routes import alerts, events, health, notifications, rules, sources

api_router = APIRouter()

# Health check at root level (not versioned)
api_router.include_router(health.router)

# All API routes under /v1
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(sources.router)
v1_router.include_router(rules.router)
v1_router.include_router(events.router)
v1_router.include_router(alerts.router)
v1_router.include_router(notifications.router)

api_router.include_router(v1_router)
