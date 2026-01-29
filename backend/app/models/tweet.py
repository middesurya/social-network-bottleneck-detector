"""Tweet model definitions."""
from typing import Optional
from pydantic import BaseModel, Field


class Tweet(BaseModel):
    """Tweet node in the social network graph."""
    
    id: str = Field(..., description="Unique tweet identifier")
    user_id: str = Field(..., description="ID of the user who posted")
    text: str = Field(..., description="Tweet content")
    created_at: Optional[str] = Field(None, description="Tweet timestamp")
    retweet_count: int = Field(0, description="Number of retweets")
    like_count: int = Field(0, description="Number of likes")
    reply_count: int = Field(0, description="Number of replies")
    quote_count: int = Field(0, description="Number of quote tweets")
    is_retweet: bool = Field(False, description="Whether this is a retweet")
    is_reply: bool = Field(False, description="Whether this is a reply")
    
    # Optional engagement metrics
    engagement_score: Optional[float] = Field(
        None, description="Computed engagement score"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "1234567890",
                "user_id": "12345",
                "text": "Just discovered an amazing new tool for network analysis!",
                "created_at": "2024-01-15T10:30:00Z",
                "retweet_count": 45,
                "like_count": 230,
                "reply_count": 12,
                "quote_count": 5,
                "is_retweet": False,
                "is_reply": False,
                "engagement_score": 0.85
            }
        }


class Mention(BaseModel):
    """Represents a mention relationship between tweet and user."""
    
    tweet_id: str
    mentioned_user_id: str


class Hashtag(BaseModel):
    """Hashtag used in tweets."""
    
    tag: str = Field(..., description="Hashtag text without #")
    usage_count: int = Field(0, description="Number of times used")
