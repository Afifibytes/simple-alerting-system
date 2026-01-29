from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Simple Alerting System"
    debug: bool = False

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/app_db"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    events_queue: str = "events"
    alerts_queue: str = "alerts"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Event settings
    event_retention_seconds: int = 7 * 24 * 60 * 60  # DB retention (7 days)
    max_events_per_evaluation: int = 10000  # Max events to load for rule evaluation (OOM protection)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
