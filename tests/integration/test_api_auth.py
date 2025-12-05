"""
Integration tests for API authentication.
"""



class TestAPIAuthentication:
    """Tests for API authentication middleware."""

    def test_health_endpoint_no_auth_required(self, client):
        """Test health endpoint works without authentication."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint_no_auth_required(self, client):
        """Test root endpoint works without authentication."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "SmartNews Learn API"

    def test_tasks_endpoint_requires_auth(self, client):
        """Test tasks endpoint requires API key."""
        response = client.get("/api/v1/tasks")

        # Should require authentication
        assert response.status_code == 401
        assert "API key is required" in response.json()["detail"]

    def test_tasks_endpoint_with_valid_key(self, client, api_headers):
        """Test tasks endpoint works with valid API key."""
        response = client.get("/api/v1/tasks", headers=api_headers)

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data

    def test_tasks_endpoint_with_invalid_key(self, client):
        """Test tasks endpoint rejects invalid API key."""
        headers = {"X-API-Key": "wrong-key"}
        response = client.get("/api/v1/tasks", headers=headers)

        assert response.status_code == 403
        assert "Invalid API key" in response.json()["detail"]

    def test_create_task_requires_auth(self, client, sample_task_request):
        """Test create task endpoint requires API key."""
        response = client.post("/api/v1/tasks", json=sample_task_request)

        assert response.status_code == 401

    def test_sources_list_no_auth_required(self, client):
        """Test sources list endpoint works without authentication."""
        response = client.get("/api/v1/sources")

        assert response.status_code == 200
        data = response.json()
        assert "sources" in data

    def test_source_videos_no_auth_required(self, client):
        """Test source videos endpoint works without authentication."""
        response = client.get("/api/v1/sources/cnn10/videos?limit=1")

        # Should work without auth (read-only)
        assert response.status_code == 200

    def test_preview_endpoint_requires_auth(self, client):
        """Test preview endpoint requires API key."""
        response = client.post(
            "/api/v1/sources/preview", json={"url": "https://youtube.com/watch?v=test"}
        )

        assert response.status_code == 401


class TestAPIHeaders:
    """Tests for API header handling."""

    def test_user_id_header_default(self, client, api_headers):
        """Test default user ID when header not provided."""
        # Remove X-User-Id from headers
        headers = {"X-API-Key": api_headers["X-API-Key"]}
        response = client.get("/api/v1/tasks", headers=headers)

        assert response.status_code == 200

    def test_user_id_header_custom(self, client, api_headers):
        """Test custom user ID from header."""
        response = client.get("/api/v1/tasks", headers=api_headers)

        assert response.status_code == 200
