import aio_pika

from app.config import settings


class RabbitMQConnection:
    """Manages a persistent async RabbitMQ connection and channel."""

    def __init__(self):
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None

    async def connect(self) -> None:
        """Establish connection to RabbitMQ."""
        self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        self._channel = await self._connection.channel()

    async def close(self) -> None:
        """Close the connection."""
        if self._channel:
            await self._channel.close()
        if self._connection:
            await self._connection.close()

    def get_channel(self) -> aio_pika.abc.AbstractChannel:
        """Get the current channel."""
        if not self._channel:
            raise RuntimeError("RabbitMQ connection not initialized")
        return self._channel


rabbitmq_connection = RabbitMQConnection()
