"""Community model definitions."""
from typing import Optional
from pydantic import BaseModel, Field


class Community(BaseModel):
    """Community detected in the social network."""
    
    id: str = Field(..., description="Unique community identifier")
    name: Optional[str] = Field(None, description="Community name/label")
    member_count: int = Field(0, description="Number of members")
    internal_edges: int = Field(0, description="Edges within community")
    external_edges: int = Field(0, description="Edges to other communities")
    modularity_contribution: Optional[float] = Field(
        None, description="This community's contribution to overall modularity"
    )
    avg_betweenness: Optional[float] = Field(
        None, description="Average betweenness of members"
    )
    avg_pagerank: Optional[float] = Field(
        None, description="Average PageRank of members"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "community_1",
                "name": "Tech Enthusiasts",
                "member_count": 150,
                "internal_edges": 2300,
                "external_edges": 450,
                "modularity_contribution": 0.15,
                "avg_betweenness": 0.023,
                "avg_pagerank": 0.0012
            }
        }


class CommunityConnection(BaseModel):
    """Connection between two communities."""
    
    source_community_id: str
    target_community_id: str
    edge_count: int = Field(..., description="Number of edges between communities")
    bridge_users: list[str] = Field(
        default_factory=list,
        description="User IDs that bridge these communities"
    )
