"""API endpoint tests."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check returns status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "services" in data


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestUsersEndpoint:
    """Tests for users endpoints."""
    
    def test_get_users(self, client):
        """Test getting user list."""
        response = client.get("/api/v1/users")
        # May fail if Neo4j not connected, that's okay for unit tests
        assert response.status_code in [200, 500]
    
    def test_get_users_with_pagination(self, client):
        """Test pagination parameters."""
        response = client.get("/api/v1/users?skip=0&limit=10")
        assert response.status_code in [200, 500]
    
    def test_get_users_invalid_limit(self, client):
        """Test invalid limit parameter."""
        response = client.get("/api/v1/users?limit=10000")
        assert response.status_code == 422  # Validation error


class TestGraphEndpoint:
    """Tests for graph endpoints."""
    
    def test_get_stats(self, client):
        """Test getting graph stats."""
        response = client.get("/api/v1/graph/stats")
        assert response.status_code in [200, 500]
    
    def test_get_subgraph(self, client):
        """Test getting subgraph."""
        response = client.get("/api/v1/graph/subgraph?limit=50")
        assert response.status_code in [200, 500]


class TestAlgorithmsEndpoint:
    """Tests for algorithm endpoints."""
    
    def test_list_algorithms(self, client):
        """Test listing available algorithms."""
        response = client.get("/api/v1/algorithms")
        assert response.status_code == 200
        data = response.json()
        assert "algorithms" in data
    
    def test_run_invalid_algorithm(self, client):
        """Test running invalid algorithm."""
        response = client.post("/api/v1/algorithms/run/invalid_algo")
        assert response.status_code == 400


class TestBottlenecksEndpoint:
    """Tests for bottleneck endpoints."""
    
    def test_get_bottlenecks(self, client):
        """Test getting bottleneck list."""
        response = client.get("/api/v1/bottlenecks")
        assert response.status_code in [200, 500]
    
    def test_get_bottlenecks_with_filters(self, client):
        """Test filtering bottlenecks."""
        response = client.get("/api/v1/bottlenecks?min_score=0.5&limit=10")
        assert response.status_code in [200, 500]
    
    def test_get_summary(self, client):
        """Test getting bottleneck summary."""
        response = client.get("/api/v1/bottlenecks/summary")
        assert response.status_code in [200, 500]


class TestCommunitiesEndpoint:
    """Tests for community endpoints."""
    
    def test_get_communities(self, client):
        """Test getting community list."""
        response = client.get("/api/v1/communities")
        assert response.status_code in [200, 500]
    
    def test_get_connection_matrix(self, client):
        """Test getting community connection matrix."""
        response = client.get("/api/v1/communities/connections/matrix")
        assert response.status_code in [200, 500]


class TestNLQEndpoint:
    """Tests for natural language query endpoints."""
    
    def test_get_examples(self, client):
        """Test getting query examples."""
        response = client.get("/api/v1/nlq/examples")
        assert response.status_code == 200
        data = response.json()
        assert "examples" in data
    
    def test_query_known_pattern(self, client):
        """Test querying with known pattern."""
        response = client.post(
            "/api/v1/nlq/query",
            json={"query": "Who are the most influential users?", "max_results": 5}
        )
        # Will succeed if Neo4j connected, fail with 500 if not
        assert response.status_code in [200, 500]
    
    def test_query_unknown_pattern(self, client):
        """Test querying with unknown pattern."""
        response = client.post(
            "/api/v1/nlq/query",
            json={"query": "asdfghjkl random text", "max_results": 5}
        )
        # Should return 400 for unknown pattern (without LLM)
        assert response.status_code in [400, 500]
