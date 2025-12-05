"""
Integration tests for API endpoints.
"""


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_returns_status(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "pending_tasks" in data

    def test_health_returns_version(self, client):
        """Test health endpoint returns version."""
        response = client.get("/health")

        data = response.json()
        assert data["version"] == "2.0.0"


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_api_info(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "SmartNews Learn API"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"


class TestSourcesEndpoint:
    """Tests for video sources endpoints."""

    def test_list_sources(self, client):
        """Test listing available sources."""
        response = client.get("/api/v1/sources")

        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert len(data["sources"]) > 0

    def test_list_sources_has_cnn10(self, client):
        """Test CNN10 is in sources list."""
        response = client.get("/api/v1/sources")

        data = response.json()
        source_ids = [s["id"] for s in data["sources"]]
        assert "cnn10" in source_ids

    def test_get_source_by_id(self, client):
        """Test getting specific source by ID."""
        response = client.get("/api/v1/sources/cnn10")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "cnn10"
        assert data["name"] == "CNN 10"

    def test_get_nonexistent_source(self, client):
        """Test getting non-existent source returns 404."""
        response = client.get("/api/v1/sources/nonexistent")

        assert response.status_code == 404

    def test_get_source_videos(self, client):
        """Test getting videos from a source."""
        response = client.get("/api/v1/sources/cnn10/videos?limit=2")

        assert response.status_code == 200
        data = response.json()
        assert data["source_id"] == "cnn10"
        assert "videos" in data


class TestTasksEndpoint:
    """Tests for tasks endpoints."""

    def test_list_tasks_empty(self, client, api_headers):
        """Test listing tasks when none exist."""
        response = client.get("/api/v1/tasks", headers=api_headers)

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data

    def test_get_nonexistent_task(self, client, api_headers):
        """Test getting non-existent task returns 404."""
        response = client.get("/api/v1/tasks/nonexistent-id", headers=api_headers)

        assert response.status_code == 404

    def test_delete_nonexistent_task(self, client, api_headers):
        """Test deleting non-existent task returns 404."""
        response = client.delete("/api/v1/tasks/nonexistent-id", headers=api_headers)

        assert response.status_code == 404


class TestErrorHandling:
    """Tests for API error handling."""

    def test_404_for_unknown_route(self, client):
        """Test 404 returned for unknown routes."""
        response = client.get("/api/v1/unknown")

        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test 405 for wrong HTTP method."""
        response = client.post("/health")

        assert response.status_code == 405

    def test_invalid_json_body(self, client, api_headers):
        """Test error handling for invalid JSON."""
        response = client.post(
            "/api/v1/tasks",
            headers=api_headers,
            content="not valid json",
        )

        assert response.status_code == 422  # Unprocessable Entity


class TestCORS:
    """Tests for CORS configuration."""

    def test_options_request(self, client):
        """Test OPTIONS request for CORS preflight."""
        response = client.options("/api/v1/tasks")

        # Should not fail (though may return 405 without CORS origin)
        assert response.status_code in [200, 405]
