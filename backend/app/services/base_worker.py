"""
Base Worker

Provides common RabbitMQ connection and message handling patterns
for all queue workers.
"""

import logging
import time
from abc import ABC, abstractmethod

import pika

from app.config import settings


class BaseWorker(ABC):
    """Base class for RabbitMQ workers with connection management and retry logic."""

    def __init__(self, worker_name: str, queue_name: str):
        self._worker_name = worker_name
        self._queue_name = queue_name
        self._connection = None
        self._channel = None
        self._logger = logging.getLogger(worker_name)

    @staticmethod
    def get_retry_count(properties) -> int:
        """Extract retry count from message headers."""
        if properties.headers and "x-retry-count" in properties.headers:
            return properties.headers["x-retry-count"]
        return 0

    def requeue_with_retry(self, ch, method, properties, body, retry_count: int, max_retries: int):
        """Requeue a message with incremented retry count, or discard if max retries reached."""
        if retry_count >= max_retries - 1:
            self._logger.warning("Max retries reached, discarding message")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        else:
            headers = dict(properties.headers) if properties.headers else {}
            headers["x-retry-count"] = retry_count + 1

            ch.basic_publish(
                exchange="",
                routing_key=self._queue_name,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent,
                    headers=headers,
                ),
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def _connect(self):
        """Connect to RabbitMQ with retry."""
        self._logger.info("Starting %s...", self._worker_name)
        self._logger.info("Connecting to RabbitMQ at %s", settings.rabbitmq_url)

        while True:
            try:
                parameters = pika.URLParameters(settings.rabbitmq_url)
                parameters.heartbeat = 600
                parameters.blocked_connection_timeout = 300
                self._connection = pika.BlockingConnection(parameters)
                break
            except pika.exceptions.AMQPConnectionError:
                self._logger.info("Waiting for RabbitMQ...")
                time.sleep(5)

        self._channel = self._connection.channel()

    @abstractmethod
    def _setup_queues(self):
        """Setup queues for consuming/publishing. Override in subclass."""
        pass

    @abstractmethod
    def _handle_message(self, ch, method, properties, body):
        """Handle a single message. Override in subclass."""
        pass

    @abstractmethod
    def _cleanup(self):
        """Clean up resources. Override in subclass."""
        pass

    def _close_connection(self):
        """Close RabbitMQ connection."""
        if self._connection and self._connection.is_open:
            try:
                self._connection.close()
            except Exception:
                pass
        self._connection = None
        self._channel = None

    def run(self):
        """Run the worker with automatic reconnection."""
        while True:
            try:
                self._connect()
                self._setup_queues()

                self._logger.info("%s ready. Waiting for messages...", self._worker_name)
                self._run_loop()

            except KeyboardInterrupt:
                self._logger.info("Shutting down %s...", self._worker_name)
                break
            except pika.exceptions.AMQPConnectionError as e:
                self._logger.warning("Connection lost: %s. Reconnecting in 5 seconds...", e)
                time.sleep(5)
            except Exception as e:
                self._logger.exception("Unexpected error: %s. Reconnecting in 5 seconds...", e)
                time.sleep(5)
            finally:
                self._cleanup()
                self._close_connection()

    def _run_loop(self):
        """Main consumption loop. Override for custom behavior (e.g., batch processing)."""
        self._channel.start_consuming()
