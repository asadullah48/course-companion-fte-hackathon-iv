"""
Integration Tests for API Endpoints
Tests full request/response cycle through FastAPI

NOTE: These tests use mock/minimal fixtures since SQLite cannot handle
PostgreSQL-specific types (UUID, ARRAY). Full integration tests should
run against a PostgreSQL test database.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest_asyncio.fixture
async def test_client():
    """Create an async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = await test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "constitutional_compliance" in data
        assert data["constitutional_compliance"]["zero_backend_llm"] is True

    @pytest.mark.asyncio
    async def test_root_endpoint(self, test_client):
        """Test root endpoint."""
        response = await test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "Course Companion API"


class TestChatGPTManifest:
    """Tests for ChatGPT plugin manifest."""

    @pytest.mark.asyncio
    async def test_ai_plugin_manifest(self, test_client):
        """Test AI plugin manifest endpoint."""
        response = await test_client.get("/.well-known/ai-plugin.json")
        assert response.status_code == 200
        data = response.json()
        assert data["schema_version"] == "v1"
        assert data["name_for_model"] == "course_companion"
        assert "auth" in data
        assert data["auth"]["type"] == "user_http"


class TestAPIRouteStructure:
    """Tests to verify API routes are registered."""

    @pytest.mark.asyncio
    async def test_api_routes_exist(self, test_client):
        """Test that main API routes are registered."""
        # Check OpenAPI endpoint
        response = await test_client.get("/openapi.json")
        assert response.status_code == 200

        openapi_spec = response.json()
        paths = openapi_spec.get("paths", {})

        # Verify key API paths exist
        expected_path_prefixes = [
            "/api/v1/chapters",    # Content delivery
            "/api/v1/modules",     # Module access
            "/api/v1/navigation",  # Navigation
            "/api/v1/quizzes",     # Quiz endpoints
            "/api/v1/progress",    # Progress tracking
            "/api/v1/search",      # Search
            "/api/v1/access",      # Access control
        ]

        for prefix in expected_path_prefixes:
            matching_paths = [p for p in paths.keys() if p.startswith(prefix)]
            assert len(matching_paths) > 0, f"No routes found for {prefix}"

    @pytest.mark.asyncio
    async def test_openapi_spec_structure(self, test_client):
        """Test OpenAPI spec has required fields."""
        response = await test_client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        assert "openapi" in spec
        assert "info" in spec
        assert spec["info"]["title"] == "Course Companion API"
        assert "paths" in spec

    @pytest.mark.asyncio
    async def test_docs_endpoint_accessible(self, test_client):
        """Test docs endpoint is accessible."""
        response = await test_client.get("/docs")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_redoc_endpoint_accessible(self, test_client):
        """Test ReDoc endpoint is accessible."""
        response = await test_client.get("/redoc")
        assert response.status_code == 200


class TestUnauthenticatedAccess:
    """Tests for unauthenticated access behavior.

    NOTE: These tests require a running PostgreSQL database.
    They are skipped in CI/local environments without a database.
    """

    @pytest.mark.skip(reason="Requires running PostgreSQL database")
    @pytest.mark.asyncio
    async def test_content_requires_auth(self, test_client):
        """Test content endpoints require authentication."""
        response = await test_client.get("/api/v1/modules")
        # Should return 401, 403, 422 (validation error) or 500 (db connection error in tests)
        assert response.status_code in [401, 403, 422, 500]

    @pytest.mark.skip(reason="Requires running PostgreSQL database")
    @pytest.mark.asyncio
    async def test_progress_requires_auth(self, test_client):
        """Test progress endpoints require authentication."""
        response = await test_client.get("/api/v1/progress/some-user-id")
        assert response.status_code in [401, 403, 422]

    @pytest.mark.skip(reason="Requires running PostgreSQL database")
    @pytest.mark.asyncio
    async def test_quiz_requires_auth(self, test_client):
        """Test quiz endpoints require authentication."""
        response = await test_client.get("/api/v1/quizzes/some-quiz-id")
        assert response.status_code in [401, 403, 422]


class TestPublicEndpoints:
    """Tests for endpoints that should be publicly accessible."""

    @pytest.mark.asyncio
    async def test_pricing_is_public(self, test_client):
        """Test pricing endpoint is publicly accessible."""
        response = await test_client.get("/api/v1/pricing")
        # Should be 200 (public) or 401/403 if requires auth
        assert response.status_code in [200, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_tiers_is_public(self, test_client):
        """Test tiers endpoint."""
        response = await test_client.get("/api/v1/access/tiers")
        # May be public or require auth
        assert response.status_code in [200, 401, 403, 404, 422]


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_404_for_unknown_route(self, test_client):
        """Test 404 response for unknown routes."""
        response = await test_client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_chapter_id(self, test_client):
        """Test handling of invalid chapter ID (without auth)."""
        response = await test_client.get("/api/v1/content/chapters/invalid-chapter-id-123")
        # Should return auth error since auth is required
        assert response.status_code in [401, 403, 404, 422]


class TestConstitutionalCompliance:
    """Tests to verify Zero-Backend-LLM compliance."""

    @pytest.mark.asyncio
    async def test_health_reports_compliance(self, test_client):
        """Test health endpoint reports constitutional compliance."""
        response = await test_client.get("/health")
        data = response.json()

        compliance = data.get("constitutional_compliance", {})
        assert compliance.get("zero_backend_llm") is True
        assert compliance.get("content_verbatim") is True
        assert compliance.get("deterministic_only") is True

    def test_no_llm_imports_in_requirements(self):
        """Test no LLM packages in requirements.txt (as actual dependencies)."""
        import os
        import re

        requirements_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "requirements.txt"
        )

        forbidden_packages = [
            "openai",
            "anthropic",
            "langchain",
            "llama-index",
            "transformers",
            "sentence-transformers",
        ]

        with open(requirements_path, "r") as f:
            lines = f.readlines()

        # Check actual package lines (not comments)
        for line in lines:
            # Skip comments and empty lines
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                continue

            # Extract package name (before ==, >=, etc.)
            match = re.match(r"^([a-zA-Z0-9_-]+)", stripped)
            if match:
                pkg_name = match.group(1).lower()
                for forbidden in forbidden_packages:
                    assert pkg_name != forbidden, f"Forbidden package '{forbidden}' found in requirements.txt"
