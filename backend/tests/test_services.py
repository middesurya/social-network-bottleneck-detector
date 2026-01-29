"""Service layer tests."""
import pytest
from unittest.mock import Mock, patch

from app.config import Settings


class TestSettings:
    """Tests for configuration settings."""
    
    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        assert settings.app_name == "Social Network Bottleneck Detector"
        assert settings.api_v1_prefix == "/api/v1"
        assert settings.neo4j_uri == "bolt://localhost:7687"
    
    def test_settings_from_env(self):
        """Test settings from environment variables."""
        with patch.dict('os.environ', {'DEBUG': 'true', 'NEO4J_PASSWORD': 'secret'}):
            settings = Settings()
            assert settings.debug == True or settings.debug == 'true'


class TestNeo4jService:
    """Tests for Neo4j service."""
    
    def test_service_initialization(self):
        """Test service can be imported."""
        from app.services.neo4j_service import Neo4jService
        service = Neo4jService()
        assert service._driver is None  # Not connected until first use
    
    def test_make_key(self):
        """Test cache key generation."""
        from app.services.cache_service import cache_service
        key1 = cache_service._make_key("test", "arg1", kwarg="value")
        key2 = cache_service._make_key("test", "arg1", kwarg="value")
        key3 = cache_service._make_key("test", "arg2", kwarg="value")
        
        # Same args should produce same key
        assert key1 == key2
        # Different args should produce different key
        assert key1 != key3
        # Key should have correct prefix
        assert key1.startswith("bottleneck:test:")


class TestBottleneckScoreCalculation:
    """Tests for bottleneck score calculation logic."""
    
    def test_score_normalization(self):
        """Test that scores are properly normalized."""
        # Bottleneck score should be between 0 and 1
        weights = {
            "betweenness": 0.4,
            "pagerank": 0.3,
            "bridge_score": 0.3
        }
        
        def calculate_score(betweenness, pagerank, bridge_score):
            return (
                weights["betweenness"] * betweenness +
                weights["pagerank"] * pagerank +
                weights["bridge_score"] * bridge_score
            )
        
        # Test extreme values
        min_score = calculate_score(0, 0, 0)
        max_score = calculate_score(1, 1, 1)
        
        assert min_score == 0
        assert max_score == 1
    
    def test_weight_sum(self):
        """Test that weights sum to 1."""
        from app.config import settings
        weights = settings.bottleneck_score_weights
        assert sum(weights.values()) == 1.0


class TestQueryPatternMatching:
    """Tests for NLQ pattern matching."""
    
    def test_pattern_matching(self):
        """Test that patterns are correctly matched."""
        from app.api.v1.nlq import match_query_pattern, QUERY_PATTERNS
        
        # Test exact matches
        assert match_query_pattern("who are the most influential users") is not None
        assert match_query_pattern("show me top bottlenecks") is not None
        
        # Test keyword-based matches
        result = match_query_pattern("find influential people")
        assert result is not None
        
        # Test no match
        result = match_query_pattern("random unrelated text xyz")
        assert result is None
    
    def test_all_patterns_have_cypher(self):
        """Test that all patterns have valid Cypher."""
        from app.api.v1.nlq import QUERY_PATTERNS
        
        for pattern_key, pattern_info in QUERY_PATTERNS.items():
            assert "cypher" in pattern_info
            assert "description" in pattern_info
            assert pattern_info["cypher"].strip() != ""


class TestResponseSchemas:
    """Tests for response schemas."""
    
    def test_user_response_schema(self):
        """Test UserResponse schema."""
        from app.schemas.responses import UserResponse
        
        user = UserResponse(
            id="test_id",
            username="testuser",
            follower_count=100,
            following_count=50
        )
        
        assert user.id == "test_id"
        assert user.username == "testuser"
        assert user.is_bottleneck == False  # Default value
    
    def test_subgraph_response_schema(self):
        """Test SubgraphResponse schema."""
        from app.schemas.responses import SubgraphResponse, CytoscapeNode, CytoscapeEdge
        
        response = SubgraphResponse(
            nodes=[
                CytoscapeNode(data={"id": "1", "label": "Node 1"})
            ],
            edges=[
                CytoscapeEdge(data={"id": "1-2", "source": "1", "target": "2"})
            ],
            metadata={"node_count": 1, "edge_count": 1}
        )
        
        assert len(response.nodes) == 1
        assert len(response.edges) == 1
        assert response.metadata["node_count"] == 1
