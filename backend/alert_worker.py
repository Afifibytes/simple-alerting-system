"""
Alert Worker

Consumes triggered alerts from RabbitMQ, creates alerts in the database,
and sends notifications to configured channels.
"""

import json
import logging
import sys
from uuid import UUID

from app.config import settings
from app.db.session import SessionLocal
from app.repositories.alert_repository import AlertRepository
from app.repositories.rule_repository import RuleRepository
from app.services.base_worker import BaseWorker
from app.services.notification_sender import NotificationSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Force unbuffered output for Docker logs
sys.stdout.reconfigure(line_buffering=True)

MAX_RETRIES = 3
ALERTS_NOTIFICATIONS_EXCHANGE = "alert_notifications"


class AlertWorker(BaseWorker):
    """Worker that consumes triggered alerts from RabbitMQ,
    creates them in the database, and sends notifications.
    """

    def __init__(self):
        super().__init__("alert-worker", settings.alerts_queue)
        self._notification_sender = None

    def _notify_clients(self, alert_id: str):
        """Publish alert notification to RabbitMQ fanout exchange for SSE clients."""
        try:
            self._channel.basic_publish(
                exchange=ALERTS_NOTIFICATIONS_EXCHANGE,
                routing_key="",  # Fanout ignores routing key
                body=alert_id,
            )
            self._logger.debug("Published alert notification: %s", alert_id)
        except Exception as e:
            self._logger.warning("Failed to publish alert notification: %s", e)

    def _get_notification_sender(self):
        """Get or create notification sender."""
        if self._notification_sender is None:
            self._notification_sender = NotificationSender()
        return self._notification_sender

    def _setup_queues(self):
        """Setup queue for consuming and fanout exchange for notifications."""
        self._channel.queue_declare(queue=self._queue_name, durable=True)
        # Fanout exchange for SSE client notifications
        self._channel.exchange_declare(
            exchange=ALERTS_NOTIFICATIONS_EXCHANGE,
            exchange_type="fanout",
            durable=False,  # Notifications are ephemeral
        )
        self._channel.basic_qos(prefetch_count=10)
        self._channel.basic_consume(
            queue=self._queue_name,
            on_message_callback=self._handle_message,
        )

    def _handle_message(self, ch, method, properties, body):
        """Process an alert message from the queue."""
        retry_count = self.get_retry_count(properties)

        try:
            alert_data = json.loads(body)
            self._logger.info("Processing alert for rule: %s", alert_data.get("rule_name"))

            db = SessionLocal()
            try:
                rule_repo = RuleRepository(db)
                rule = rule_repo.get_by_id(UUID(alert_data["rule_id"]))

                if not rule:
                    self._logger.warning("Rule %s not found, discarding alert", alert_data["rule_id"])
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                alert_repo = AlertRepository(db)
                alert = alert_repo.create(
                    rule=rule,
                    matches_count=alert_data["matches_count"],
                    message=alert_data["message"],
                )
                self._logger.info("Alert created: %s (rule: %s)", alert.id, rule.name)

                # Notify SSE clients
                self._notify_clients(str(alert.id))

                if rule.notification_channels:
                    self._logger.debug("Sending notifications to %d channels", len(rule.notification_channels))
                    sender = self._get_notification_sender()
                    results = sender.send_alert(alert, rule)
                    self._logger.debug("Notification results: %s", results)

                ch.basic_ack(delivery_tag=method.delivery_tag)

            finally:
                db.close()

        except json.JSONDecodeError as e:
            self._logger.warning("Invalid JSON, discarding message: %s", e)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            self._logger.error("Error processing alert (attempt %d/%d): %s", retry_count + 1, MAX_RETRIES, e)
            self.requeue_with_retry(ch, method, properties, body, retry_count, MAX_RETRIES)

    def _cleanup(self):
        """Clean up resources."""
        if self._notification_sender:
            try:
                self._notification_sender.close()
            except Exception:
                pass
        self._notification_sender = None


def main():
    worker = AlertWorker()
    worker.run()


if __name__ == "__main__":
    main()
