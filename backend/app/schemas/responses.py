"""API response schemas."""
from typing import Any, Optional
from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """Single user response."""
    
    id: str
    username: str
    display_name: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    
    # Metrics
    betweenness_centrality: Optional[float] = None
    pagerank: Optional[float] = None
    bottleneck_score: Optional[float] = None
    community_id: Optional[str] = None
    is_bottleneck: bool = False


class UsersListResponse(BaseModel):
    """Paginated users list response."""
    
    users: list[UserResponse]
    total: int
    skip: int
    limit: int


class GraphStatsResponse(BaseModel):
    """Graph statistics response."""
    
    user_count: int = 0
    follows_count: int = 0
    community_count: int = 0
    tweet_count: int = 0
    avg_followers: Optional[float] = None
    avg_following: Optional[float] = None
    density: Optional[float] = None


class BottleneckResponse(BaseModel):
    """Bottleneck node response."""
    
    user: UserResponse
    bottleneck_score: float
    betweenness_centrality: float
    bridge_score: float
    connected_communities: list[str] = []
    influence_radius: int = 0


class CommunityResponse(BaseModel):
    """Community response."""
    
    id: str
    name: Optional[str] = None
    member_count: int
    top_members: list[UserResponse] = []
    internal_density: Optional[float] = None
    external_connections: int = 0


class CytoscapeNode(BaseModel):
    """Cytoscape.js node format."""
    
    data: dict[str, Any]
    position: Optional[dict[str, float]] = None
    classes: Optional[str] = None


class CytoscapeEdge(BaseModel):
    """Cytoscape.js edge format."""
    
    data: dict[str, Any]
    classes: Optional[str] = None


class SubgraphResponse(BaseModel):
    """Subgraph response in Cytoscape.js format."""
    
    nodes: list[CytoscapeNode]
    edges: list[CytoscapeEdge]
    metadata: dict[str, Any] = Field(default_factory=dict)


class AlgorithmRunResponse(BaseModel):
    """Algorithm execution response."""
    
    algorithm: str
    status: str
    execution_time_ms: float
    nodes_processed: int
    results_summary: dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None


class NLQResponse(BaseModel):
    """Natural language query response."""
    
    query: str
    generated_cypher: str
    results: list[dict[str, Any]]
    explanation: Optional[str] = None
    confidence: Optional[float] = None
