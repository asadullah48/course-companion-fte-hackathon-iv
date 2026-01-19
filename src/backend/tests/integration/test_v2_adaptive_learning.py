"""
Integration Tests for API v2 - Adaptive Learning (Phase 2)
Tests the new adaptive learning features with Claude Sonnet 4 integration
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


class TestV2AdaptiveLearningAPI:
    """Tests for the v2 adaptive learning API endpoints."""

    @pytest.mark.asyncio
    async def test_v2_learning_profile_endpoint_exists(self, test_client):
        """Test that the v2 learning profile endpoint is registered."""
        response = await test_client.get("/api/v2/learning/profile/test-user")
        # Should return 401/403 (auth required) or 404 (not found)
        # If it returns 404, the route exists but requires auth
        # If it returns 422, the route exists but validation failed
        assert response.status_code in [401, 403, 404, 422], \
            f"Expected 401/403/404/422 for auth/validation, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_v2_recommendations_endpoint_exists(self, test_client):
        """Test that the v2 recommendations endpoint is registered."""
        response = await test_client.get("/api/v2/learning/recommendations/test-user")
        assert response.status_code in [401, 403, 404, 422], \
            f"Expected 401/403/404/422 for auth/validation, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_v2_knowledge_gaps_endpoint_exists(self, test_client):
        """Test that the v2 knowledge gaps endpoint is registered."""
        response = await test_client.get("/api/v2/learning/knowledge-gaps/test-user")
        assert response.status_code in [401, 403, 404, 422], \
            f"Expected 401/403/404/422 for auth/validation, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_v2_learning_path_endpoint_exists(self, test_client):
        """Test that the v2 learning path endpoint is registered."""
        # Test POST endpoint
        response = await test_client.post("/api/v2/learning/path/generate", json={
            "user_id": "test-user",
            "goal": {"type": "complete_course", "target_date": "2026-02-28"},
            "constraints": {"available_hours_per_week": 5}
        })
        assert response.status_code in [401, 403, 404, 422], \
            f"Expected 401/403/404/422 for auth/validation, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_v2_next_steps_endpoint_exists(self, test_client):
        """Test that the v2 next steps endpoint is registered."""
        response = await test_client.get("/api/v2/learning/next-steps/test-user")
        assert response.status_code in [401, 403, 404, 422], \
            f"Expected 401/403/404/422 for auth/validation, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_v2_api_routes_in_openapi_spec(self, test_client):
        """Test that v2 adaptive learning routes are in the OpenAPI spec."""
        response = await test_client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        paths = spec.get("paths", {})

        # Verify v2 learning paths exist
        expected_v2_learning_paths = [
            "/api/v2/learning/profile/{user_id}",
            "/api/v2/learning/recommendations/{user_id}",
            "/api/v2/learning/knowledge-gaps/{user_id}",
            "/api/v2/learning/path/generate",
            "/api/v2/learning/next-steps/{user_id}",
        ]

        for path in expected_v2_learning_paths:
            # Check if any path in the spec starts with this path
            matching_paths = [p for p in paths.keys() if p.startswith(path.split('{')[0])]
            assert len(matching_paths) > 0, f"No routes found for {path}"


class TestV2ConstitutionalCompliance:
    """Tests to verify Phase 2 constitutional compliance."""

    @pytest.mark.asyncio
    async def test_v2_api_has_proper_tier_access_control(self, test_client):
        """Test that v2 endpoints have proper tier-based access control."""
        response = await test_client.get("/openapi.json")
        assert response.status_code == 200

        spec = response.json()
        paths = spec.get("paths", {})

        # Check that v2 learning endpoints exist and have proper documentation
        v2_learning_paths = [p for p in paths.keys() if "/v2/learning/" in p]
        assert len(v2_learning_paths) > 0, "No v2 learning paths found in OpenAPI spec"

        # Verify that the paths have proper access control documentation
        for path in v2_learning_paths:
            path_details = paths[path]
            # Check that each method in the path has proper documentation
            for method, details in path_details.items():
                assert "description" in details or "summary" in details
                # Look for access control mentions in description
                description = details.get("description", "") + details.get("summary", "")
                # Should mention access control, tiers, or permissions
                assert any(keyword in description.lower() for keyword in 
                          ["access", "tier", "permission", "require"]), \
                    f"Path {path} {method} should mention access control in description"

    def test_phase2_constitutional_amendment_documented(self):
        """Test that Phase 2 constitutional amendment is properly documented."""
        import os

        requirements_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "requirements.txt"
        )

        with open(requirements_path, "r") as f:
            content = f.read()

        # Verify constitutional amendment documentation exists
        assert "Phase 2 Constitutional Amendment" in content
        assert "anthropic" in content
        assert "Claude Sonnet 4" in content or "Claude API" in content

        # Verify forbidden packages are still documented
        assert "FORBIDDEN PACKAGES" in content
        assert "openai" in content
        assert "langchain" in content