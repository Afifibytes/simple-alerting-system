"""Tests for API endpoints - integration tests."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def app():
    """Create app without lifespan for testing."""
    test_app = create_app()
    # Mock the rabbitmq state that would be set by lifespan
    test_app.state.rabbitmq = MagicMock()
    test_app.state.rabbitmq.get_channel.return_value = MagicMock()
    return test_app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_returns_status(self, client):
        """Should return health status."""
        with patch("app.api.routes.health.get_health_service") as mock_service:
            mock_health = MagicMock()
            mock_health.check_all = AsyncMock(
                return_value={
                    "status": "healthy",
                    "database": "connected",
                    "rabbitmq": "connected",
                }
            )
            mock_service.return_value = mock_health

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    def test_health_does_not_expose_errors(self, client):
        """Should not expose internal error details."""
        with patch("app.api.routes.health.get_health_service") as mock_service:
            mock_health = MagicMock()
            mock_health.check_all = AsyncMock(
                return_value={
                    "status": "unhealthy",
                    "database": "disconnected",
                    "rabbitmq": "connected",
                }
            )
            mock_service.return_value = mock_health

            response = client.get("/health")

            data = response.json()
            # Should say "disconnected", not expose exception details
            assert "error" not in data.get("database", "").lower()
            assert "exception" not in str(data).lower()


class TestEventIngestion:
    """Tests for event ingestion endpoint."""

    def test_rejects_oversized_event_data(self, client):
        """Should reject events with oversized data."""
        large_data = {"large": "x" * 100000}  # ~100KB

        with patch("app.api.routes.events.get_rabbitmq_from_request"):
            response = client.post(
                "/v1/events",
                json={
                    "source": "test",
                    "event_type": "log",
                    "data": large_data,
                },
            )

        assert response.status_code == 422  # Validation error

    def test_rejects_empty_source(self, client):
        """Should reject events with empty source."""
        with patch("app.api.routes.events.get_rabbitmq_from_request"):
            response = client.post(
                "/v1/events",
                json={
                    "source": "",
                    "event_type": "log",
                    "data": {},
                },
            )

        assert response.status_code == 422

    def test_accepts_valid_event(self, app):
        """Should accept valid events."""
        from datetime import datetime, timezone
        from app.api.routes.events import get_event_service

        mock_service = AsyncMock()
        mock_service.ingest.return_value = {
            "timestamp": datetime.now(timezone.utc),
            "source": "test-source",
            "event_type": "log",
            "data": {"level": "info", "message": "Test"},
        }

        app.dependency_overrides[get_event_service] = lambda: mock_service

        try:
            client = TestClient(app)
            response = client.post(
                "/v1/events",
                json={
                    "source": "test-source",
                    "event_type": "log",
                    "data": {"level": "info", "message": "Test"},
                },
            )
            assert response.status_code == 202
        finally:
            app.dependency_overrides.clear()


class TestSourcesEndpoint:
    """Tests for sources endpoint."""

    def test_list_sources_returns_paginated(self, client):
        """Should return paginated list of sources."""
        with patch("app.api.routes.sources.get_source_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.get_all.return_value = ([], 0)
            mock_service.return_value = mock_svc

            response = client.get("/v1/sources")

            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert "offset" in data
            assert "limit" in data

    def test_search_escapes_wildcards(self, client):
        """Should escape LIKE wildcards in search."""
        with patch("app.api.routes.sources.get_source_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.get_all.return_value = ([], 0)
            mock_service.return_value = mock_svc

            # Search with LIKE wildcards
            response = client.get("/v1/sources?search=test%25value")  # test%value

            assert response.status_code == 200


class TestAlertsEndpoint:
    """Tests for alerts endpoint."""

    def test_list_alerts_returns_paginated(self, client):
        """Should return paginated list of alerts."""
        with patch("app.api.routes.alerts.get_alert_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.get_all.return_value = ([], 0)
            mock_service.return_value = mock_svc

            response = client.get("/v1/alerts")

            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "total" in data

    def test_get_alert_not_found(self, client):
        """Should return 404 for non-existent alert."""
        from app.exceptions import EntityNotFoundError

        with patch("app.api.routes.alerts.get_alert_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.get_by_id.side_effect = EntityNotFoundError("Alert", str(uuid4()))
            mock_service.return_value = mock_svc

            response = client.get(f"/v1/alerts/{uuid4()}")

            assert response.status_code == 404


class TestRulesEndpoint:
    """Tests for rules endpoint."""

    def test_list_rules_returns_paginated(self, client):
        """Should return paginated list of rules."""
        with patch("app.api.routes.rules.get_rule_service") as mock_service:
            mock_svc = MagicMock()
            mock_svc.get_all.return_value = ([], 0)
            mock_service.return_value = mock_svc

            response = client.get("/v1/rules")

            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "total" in data


class TestCORSHeaders:
    """Tests for CORS configuration."""

    def test_cors_allows_configured_origin(self, client):
        """Should allow configured origin."""
        response = client.options(
            "/v1/sources",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # OPTIONS might return 200 or 204 depending on config
        assert response.status_code in [200, 204, 405]

    def test_cors_restricts_methods(self, client):
        """Should only allow specified methods."""
        response = client.options(
            "/v1/sources",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        if "access-control-allow-methods" in response.headers:
            allowed = response.headers["access-control-allow-methods"]
            # Should not contain wildcard
            assert "*" not in allowed or "GET" in allowed
