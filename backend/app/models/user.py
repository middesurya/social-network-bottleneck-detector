"""User model definitions."""
from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    """User node in the social network graph."""
    
    id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Twitter handle")
    display_name: Optional[str] = Field(None, description="Display name")
    bio: Optional[str] = Field(None, description="User bio/description")
    follower_count: int = Field(0, description="Number of followers")
    following_count: int = Field(0, description="Number of accounts following")
    tweet_count: int = Field(0, description="Total tweets")
    verified: bool = Field(False, description="Verified account status")
    created_at: Optional[str] = Field(None, description="Account creation date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "12345",
                "username": "johndoe",
                "display_name": "John Doe",
                "bio": "Software engineer and tech enthusiast",
                "follower_count": 1500,
                "following_count": 500,
                "tweet_count": 2300,
                "verified": False,
                "created_at": "2020-01-15"
            }
        }


class UserInDB(User):
    """User with computed graph metrics stored in database."""
    
    # Centrality metrics
    betweenness_centrality: Optional[float] = Field(
        None, description="Betweenness centrality score"
    )
    pagerank: Optional[float] = Field(
        None, description="PageRank score"
    )
    degree_centrality: Optional[float] = Field(
        None, description="Degree centrality score"
    )
    
    # Community detection
    community_id: Optional[str] = Field(
        None, description="ID of the community this user belongs to"
    )
    
    # Bottleneck metrics
    bottleneck_score: Optional[float] = Field(
        None, description="Composite bottleneck score (0-1)"
    )
    bridge_score: Optional[float] = Field(
        None, description="Score indicating how much user bridges communities"
    )
    is_bottleneck: bool = Field(
        False, description="Whether user is classified as a bottleneck"
    )


class UserConnection(BaseModel):
    """Represents a connection between users."""
    
    source_id: str
    target_id: str
    relationship_type: str = "FOLLOWS"
    weight: float = 1.0
    created_at: Optional[str] = None
