"""
Event Worker

Consumes events from RabbitMQ, persists to PostgreSQL, and evaluates rules.
Triggered alerts are published to a separate queue for async processing.
"""

import json
import logging
import sys
import time
from datetime import datetime, timezone

import pika

from app.config import settings
from app.db.session import SessionLocal
from app.repositories.event_repository import EventRepository
from app.repositories.rule_repository import RuleRepository
from app.repositories.source_repository import SourceRepository
from app.services.base_worker import BaseWorker
from app.services.rule_evaluator import RuleEvaluator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Force unbuffered output for Docker logs
sys.stdout.reconfigure(line_buffering=True)

MAX_RETRIES = 3
BATCH_SIZE = 100
FLUSH_INTERVAL_SECONDS = 5


class EventWorker(BaseWorker):
    """Worker that consumes events from RabbitMQ, stores in DB, and evaluates rules.

    Events are buffered and flushed in batches for efficiency.
    Triggered alerts are published to alerts queue for async processing.
    """

    def __init__(self):
        super().__init__("event-worker", settings.events_queue)
        self._event_buffer = []
        self._pending_acks = []
        self._last_flush_time = time.time()

    # -------------------------------------------------------------------------
    # Queue Setup
    # -------------------------------------------------------------------------

    def _setup_queues(self):
        """Setup queues for consuming and publishing."""
        self._channel.queue_declare(queue=self._queue_name, durable=True)
        self._channel.queue_declare(queue=settings.alerts_queue, durable=True)
        self._channel.basic_qos(prefetch_count=BATCH_SIZE)
        self._channel.basic_consume(
            queue=self._queue_name,
            on_message_callback=self._handle_message,
        )

    # -------------------------------------------------------------------------
    # Message Handling
    # -------------------------------------------------------------------------

    def _handle_message(self, ch, method, properties, body):
        """Buffer incoming message for batch processing."""
        retry_count = self.get_retry_count(properties)

        try:
            event_data = json.loads(body)
            buffered_event = self._parse_event(event_data)
            self._buffer_event(buffered_event, method.delivery_tag)

            if self._should_flush():
                self._flush_batch(ch)

        except json.JSONDecodeError as e:
            self._logger.warning("Invalid JSON, discarding message: %s", e)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            self._logger.error("Error buffering event (attempt %d/%d): %s", retry_count + 1, MAX_RETRIES, e)
            self.requeue_with_retry(ch, method, properties, body, retry_count, MAX_RETRIES)

    def _parse_event(self, event_data: dict) -> dict:
        """Parse raw event data into buffered event format."""
        timestamp = self._parse_timestamp(event_data.get("timestamp"))
        return {
            "source_name": event_data["source"],
            "event_type": event_data["event_type"],
            "data": event_data.get("data", {}),
            "timestamp": timestamp,
            "raw_data": event_data,
        }

    def _parse_timestamp(self, timestamp_str: str | None) -> datetime:
        """Parse ISO timestamp string or return current UTC time."""
        if timestamp_str:
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return datetime.now(timezone.utc)

    def _buffer_event(self, event: dict, delivery_tag: int):
        """Add event to buffer and track its delivery tag for acknowledgment."""
        self._event_buffer.append(event)
        self._pending_acks.append(delivery_tag)

    # -------------------------------------------------------------------------
    # Batch Flushing
    # -------------------------------------------------------------------------

    def _should_flush(self) -> bool:
        """Check if buffer should be flushed based on size or time."""
        batch_full = len(self._event_buffer) >= BATCH_SIZE
        time_elapsed = time.time() - self._last_flush_time >= FLUSH_INTERVAL_SECONDS
        return batch_full or time_elapsed

    def _flush_batch(self, ch):
        """Flush buffered events: persist to DB, evaluate rules, send acks."""
        if not self._event_buffer:
            self._last_flush_time = time.time()
            return

        events_to_flush, acks_to_send = self._take_buffer_snapshot()

        try:
            self._persist_events(events_to_flush)
            affected_sources = self._extract_source_names(events_to_flush)
            self._evaluate_rules_for_sources(affected_sources, ch)
            self._acknowledge_messages(ch, acks_to_send)
            self._logger.info("Flushed batch of %d events", len(events_to_flush))
        except Exception as e:
            self._logger.exception("Error flushing batch: %s", e)
            self._reject_messages(ch, acks_to_send)

    def _take_buffer_snapshot(self) -> tuple[list[dict], list[int]]:
        """Take snapshot of buffer and clear it for next batch."""
        events = self._event_buffer[:]
        acks = self._pending_acks[:]
        self._event_buffer.clear()
        self._pending_acks.clear()
        self._last_flush_time = time.time()
        return events, acks

    def _persist_events(self, events: list[dict]):
        """Persist events to database."""
        db = SessionLocal()
        try:
            repo = EventRepository(db)
            count = repo.create_batch(events)
            self._logger.info("Batch persisted %d events to database", count)
        finally:
            db.close()

    def _extract_source_names(self, events: list[dict]) -> set[str]:
        """Extract unique source names from events."""
        return {event["source_name"] for event in events}

    def _acknowledge_messages(self, ch, delivery_tags: list[int]):
        """Send acknowledgments for processed messages."""
        for tag in delivery_tags:
            ch.basic_ack(delivery_tag=tag)

    def _reject_messages(self, ch, delivery_tags: list[int]):
        """Reject messages and requeue them for retry."""
        for tag in delivery_tags:
            try:
                ch.basic_nack(delivery_tag=tag, requeue=True)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # Rule Evaluation
    # -------------------------------------------------------------------------

    def _evaluate_rules_for_sources(self, source_names: set[str], channel):
        """Evaluate rules for affected sources and publish triggered alerts."""
        self._logger.info("Evaluating rules for sources: %s", source_names)
        db = SessionLocal()
        try:
            rule_repo = RuleRepository(db)
            source_repo = SourceRepository(db)
            evaluator = RuleEvaluator(db)

            for source_name in source_names:
                self._evaluate_source_rules(
                    source_name, source_repo, rule_repo, evaluator, channel
                )
        except Exception as e:
            self._logger.exception("Error in rule evaluation: %s", e)
        finally:
            db.close()

    def _evaluate_source_rules(self, source_name, source_repo, rule_repo, evaluator, channel):
        """Evaluate all rules for a single source."""
        source = source_repo.get_by_name(source_name)
        if not source:
            self._logger.debug("Source '%s' not found in database, skipping", source_name)
            return

        self._logger.debug("Found source '%s' (ID: %s)", source_name, source.id)
        rules = rule_repo.get_by_source_id(source.id, active_only=True)
        self._logger.debug("Found %d active rules for source '%s'", len(rules), source_name)

        for rule in rules:
            self._evaluate_single_rule(rule, source_name, evaluator, channel)

    def _evaluate_single_rule(self, rule, source_name, evaluator, channel):
        """Evaluate a single rule and publish alert if triggered."""
        try:
            result = evaluator.evaluate(rule)
            self._logger.debug(
                "Rule '%s': %d matches, threshold=%d, triggered=%s",
                rule.name, result.matches, result.threshold, result.triggered
            )

            if result.triggered:
                self._publish_alert(rule, source_name, result, channel)

        except Exception as e:
            self._logger.error("Error evaluating rule '%s': %s", rule.name, e)

    def _publish_alert(self, rule, source_name, result, channel):
        """Publish triggered alert to the alerts queue."""
        alert_data = self._build_alert_data(rule, source_name, result)
        channel.basic_publish(
            exchange="",
            routing_key=settings.alerts_queue,
            body=json.dumps(alert_data),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
            ),
        )
        self._logger.info("Published alert to queue for rule: %s", rule.name)

    def _build_alert_data(self, rule, source_name, result) -> dict:
        """Build alert payload for publishing."""
        return {
            "rule_id": str(rule.id),
            "rule_name": rule.name,
            "source_name": source_name,
            "severity": rule.severity,
            "matches_count": result.matches,
            "message": result.message,
            "notification_channel_ids": [str(c.id) for c in rule.notification_channels],
            "triggered_at": datetime.now(timezone.utc).isoformat(),
        }

    # -------------------------------------------------------------------------
    # Run Loop & Cleanup
    # -------------------------------------------------------------------------

    def _run_loop(self):
        """Main event loop with periodic buffer flushing."""
        self._logger.info("Batch size: %d, flush interval: %ds", BATCH_SIZE, FLUSH_INTERVAL_SECONDS)
        while True:
            self._connection.process_data_events(time_limit=FLUSH_INTERVAL_SECONDS)
            if self._event_buffer and self._should_flush():
                self._flush_batch(self._channel)

    def _cleanup(self):
        """Flush remaining events before shutdown."""
        if self._event_buffer and self._channel:
            try:
                self._logger.info("Flushing remaining events...")
                self._flush_batch(self._channel)
            except Exception:
                pass


def main():
    worker = EventWorker()
    worker.run()


if __name__ == "__main__":
    main()
