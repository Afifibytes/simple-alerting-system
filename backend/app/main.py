from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config import settings
from app.exceptions import (
    AlertingSystemError,
    DatabaseError,
    EntityNotFoundError,
    MessageQueueError,
)
from app.infrastructure.rabbitmq import rabbitmq_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbitmq_connection.connect()
    app.state.rabbitmq = rabbitmq_connection
    yield
    # Shutdown: close connections
    await rabbitmq_connection.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="An alerting system with rule management, event ingestion, and alert evaluation.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Exception handlers
    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(
        request: Request, exc: EntityNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(DatabaseError)
    async def database_error_handler(
        request: Request, exc: DatabaseError
    ) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": "Database error occurred"})

    @app.exception_handler(MessageQueueError)
    async def message_queue_error_handler(
        request: Request, exc: MessageQueueError
    ) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": "Message queue unavailable"})

    @app.exception_handler(AlertingSystemError)
    async def alerting_system_error_handler(
        request: Request, exc: AlertingSystemError
    ) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": exc.message})

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "Accept"],
    )

    # Include API routes
    app.include_router(api_router)

    @app.get("/", tags=["Root"])
    async def root():
        return {"message": "Simple Alerting System API", "version": "1.0.0"}

    return app


app = create_app()
