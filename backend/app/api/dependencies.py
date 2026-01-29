from typing import Generator

from fastapi import Request
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.infrastructure.rabbitmq import RabbitMQConnection


def get_db() -> Generator[Session, None, None]:
    """Yield a database session with proper cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_rabbitmq_from_request(request: Request) -> RabbitMQConnection:
    """Get RabbitMQ connection from app state."""
    return request.app.state.rabbitmq
