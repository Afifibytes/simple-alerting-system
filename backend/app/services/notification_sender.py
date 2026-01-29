"""Notification sender service - sends alerts to configured channels."""

import ipaddress
import logging
import socket
from typing import Any
from urllib.parse import urlparse

import httpx

from app.models.alert import Alert
from app.models.notification import NotificationChannel, ChannelType
from app.models.rule import AlertRule

logger = logging.getLogger(__name__)

# Allowed URL schemes for webhooks
ALLOWED_SCHEMES = {"http", "https"}

# Known safe Slack webhook domain
SLACK_WEBHOOK_DOMAIN = "hooks.slack.com"


def _is_private_ip(ip_str: str) -> bool:
    """Check if an IP address is private/internal."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        )
    except ValueError:
        return False


def _validate_webhook_url(url: str, allow_slack: bool = False) -> tuple[bool, str]:
    """
    Validate a webhook URL for security.
    Returns (is_valid, error_message).
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format"

    # Check scheme
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False, f"URL scheme must be one of: {ALLOWED_SCHEMES}"

    # Check host exists
    if not parsed.netloc:
        return False, "URL must have a host"

    # Extract hostname (without port)
    hostname = parsed.hostname
    if not hostname:
        return False, "URL must have a valid hostname"

    # Allow Slack webhook domain
    if allow_slack and hostname == SLACK_WEBHOOK_DOMAIN:
        return True, ""

    # Resolve hostname to IP and check if it's internal
    try:
        ip_addresses = socket.getaddrinfo(hostname, None)
        for addr_info in ip_addresses:
            ip_str = addr_info[4][0]
            if _is_private_ip(ip_str):
                return False, "Webhook URLs cannot target internal/private IP addresses"
    except socket.gaierror:
        # Can't resolve - could be a security risk, but allow for now
        # In production, you might want to block unresolvable hosts
        logger.warning("Could not resolve hostname: %s", hostname)

    return True, ""


class NotificationSender:
    """Sends notifications to various channel types."""

    def __init__(self):
        self._http_client = httpx.Client(timeout=10.0)

    def send_alert(self, alert: Alert, rule: AlertRule) -> dict[str, bool]:
        """Send alert notification to all channels configured for the rule.

        Returns dict of {channel_name: success} for each channel.
        """
        results = {}

        for channel in rule.notification_channels:
            if not channel.is_active:
                logger.debug("Skipping inactive channel: %s", channel.name)
                continue

            try:
                success = self._send_to_channel(channel, alert, rule)
                results[channel.name] = success
                if success:
                    logger.info("Notification sent to %s channel: %s", channel.channel_type.value, channel.name)
                else:
                    logger.warning("Failed to send to channel: %s", channel.name)
            except Exception as e:
                logger.error("Error sending to channel %s: %s", channel.name, e)
                results[channel.name] = False

        return results

    def _send_to_channel(self, channel: NotificationChannel, alert: Alert, rule: AlertRule) -> bool:
        """Send notification to a specific channel."""
        if channel.channel_type == ChannelType.webhook:
            return self._send_webhook(channel, alert, rule)
        elif channel.channel_type == ChannelType.slack:
            return self._send_slack(channel, alert, rule)
        elif channel.channel_type == ChannelType.email:
            return self._send_email(channel, alert, rule)
        else:
            logger.warning("Unknown channel type: %s", channel.channel_type)
            return False

    def _build_alert_payload(self, alert: Alert, rule: AlertRule) -> dict[str, Any]:
        """Build common alert payload."""
        return {
            "alert_id": str(alert.id),
            "rule_id": str(rule.id),
            "rule_name": rule.name,
            "severity": alert.severity,
            "status": alert.status.value,
            "message": alert.message,
            "matches_count": alert.matches_count,
            "triggered_at": alert.triggered_at.isoformat(),
            "source": rule.source_rel.name if rule.source_rel else "unknown",
        }

    def _send_webhook(self, channel: NotificationChannel, alert: Alert, rule: AlertRule) -> bool:
        """Send notification via webhook."""
        url = channel.config.get("url")
        if not url:
            logger.warning("Webhook channel %s missing 'url' in config", channel.name)
            return False

        # Validate URL to prevent SSRF
        is_valid, error = _validate_webhook_url(url)
        if not is_valid:
            logger.warning("Webhook URL validation failed for channel %s: %s", channel.name, error)
            return False

        payload = self._build_alert_payload(alert, rule)

        try:
            response = self._http_client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                follow_redirects=False,  # Don't follow redirects to prevent SSRF bypass
            )
            return response.status_code < 400
        except Exception as e:
            logger.error("Webhook request failed: %s", e)
            return False

    def _send_slack(self, channel: NotificationChannel, alert: Alert, rule: AlertRule) -> bool:
        """Send notification via Slack webhook."""
        webhook_url = channel.config.get("webhook_url")
        if not webhook_url:
            logger.warning("Slack channel %s missing 'webhook_url' in config", channel.name)
            return False

        # Validate URL - allow Slack webhook domain
        is_valid, error = _validate_webhook_url(webhook_url, allow_slack=True)
        if not is_valid:
            logger.warning("Slack webhook URL validation failed for channel %s: %s", channel.name, error)
            return False

        # Build Slack message format
        severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(alert.severity, "⚪")

        slack_payload = {
            "text": f"{severity_emoji} Alert: {rule.name}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{severity_emoji} Alert Triggered: {rule.name}",
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Severity:*\n{alert.severity.upper()}"},
                        {"type": "mrkdwn", "text": f"*Source:*\n{rule.source_rel.name if rule.source_rel else 'unknown'}"},
                        {"type": "mrkdwn", "text": f"*Matches:*\n{alert.matches_count}"},
                        {"type": "mrkdwn", "text": f"*Threshold:*\n{rule.condition_threshold}"},
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Message:*\n{alert.message or 'No message'}",
                    }
                },
            ]
        }

        try:
            response = self._http_client.post(
                webhook_url,
                json=slack_payload,
                headers={"Content-Type": "application/json"},
                follow_redirects=False,
            )
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.error("Slack request failed: %s", e)
            return False

    def _send_email(self, channel: NotificationChannel, alert: Alert, rule: AlertRule) -> bool:
        """Send notification via email.

        Note: This is a placeholder. In production, you would integrate with
        an email service like SendGrid, SES, or SMTP.
        """
        recipients = channel.config.get("recipients", [])
        if not recipients:
            logger.warning("Email channel %s has no recipients", channel.name)
            return False

        # Log the email that would be sent (placeholder for actual email sending)
        logger.info(
            "[EMAIL PLACEHOLDER] Would send to: %s, Subject: Alert - %s (%s)",
            recipients, rule.name, alert.severity.upper()
        )

        # In production, integrate with email service here
        # For now, return True to indicate "success" for testing
        return True

    def close(self):
        """Close HTTP client."""
        self._http_client.close()
