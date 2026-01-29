"""Natural Language Query endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import logging

from app.services.neo4j_service import neo4j_service
from app.services.nlq_service import nlq_service, match_query_pattern, QUERY_PATTERNS
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class NLQRequest(BaseModel):
    """Natural language query request."""
    query: str = Field(..., description="Natural language question about the graph")
    max_results: int = Field(10, ge=1, le=100, description="Maximum results to return")
    use_llm: bool = Field(True, description="Use LLM for query generation (falls back to patterns if unavailable)")


class NLQResponse(BaseModel):
    """Natural language query response."""
    query: str
    generated_cypher: str
    results: list
    explanation: Optional[str] = None
    confidence: float
    used_llm: bool = False


@router.post("/query", response_model=NLQResponse)
async def natural_language_query(request: NLQRequest):
    """
    Convert a natural language question to Cypher and execute it.
    
    Uses GPT-4 for query generation when available, falls back to pattern matching.
    
    Example questions:
    - "Who are the top bottlenecks?"
    - "Show me the most influential users"
    - "Find users that bridge multiple communities"
    - "What is the largest community?"
    - "Show connections between communities"
    """
    cypher = None
    confidence = 0.0
    explanation = None
    used_llm = False
    
    # Try LLM-based generation first if enabled and available
    if request.use_llm and nlq_service.is_available():
        try:
            cypher, confidence = nlq_service.generate_cypher(request.query)
            if cypher:
                used_llm = True
                explanation = "Query generated using GPT-4"
        except Exception as e:
            logger.warning(f"LLM query generation failed: {e}, falling back to patterns")
    
    # Fall back to pattern matching
    if not cypher:
        pattern = match_query_pattern(request.query)
        if pattern:
            cypher = pattern["cypher"]
            explanation = pattern["description"]
            confidence = 0.9
        else:
            # Last resort: try a generic search
            cypher = """
                MATCH (u:User)
                WHERE u.username CONTAINS $search OR u.display_name CONTAINS $search
                RETURN u LIMIT $limit
            """
            explanation = "Generic user search"
            confidence = 0.5
    
    # Ensure limit parameter
    if "$limit" not in cypher.lower():
        cypher = cypher.rstrip().rstrip(";") + f" LIMIT {request.max_results}"
    
    # Execute the query
    try:
        params = {"limit": request.max_results, "search": request.query.split()[-1] if confidence < 0.6 else ""}
        results = neo4j_service.execute_query(cypher, params)
        
        return NLQResponse(
            query=request.query,
            generated_cypher=cypher.strip(),
            results=results,
            explanation=explanation,
            confidence=confidence,
            used_llm=used_llm
        )
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Query execution failed: {str(e)}. Try rephrasing your question."
        )


@router.get("/patterns")
async def list_query_patterns():
    """List available query patterns for natural language queries."""
    patterns = []
    for key, data in QUERY_PATTERNS.items():
        patterns.append({
            "pattern": key,
            "description": data["description"],
            "example_query": f"Show me {key}"
        })
    
    return {
        "patterns": patterns,
        "llm_available": nlq_service.is_available(),
        "note": "When LLM is available, you can ask any question in natural language"
    }


@router.get("/examples")
async def get_query_examples():
    """Get example natural language queries."""
    return {
        "examples": [
            {
                "question": "Who are the top bottlenecks?",
                "description": "Find users critical for network connectivity"
            },
            {
                "question": "Show me the most influential users",
                "description": "Find users with highest PageRank scores"
            },
            {
                "question": "Find users that bridge multiple communities",
                "description": "Identify cross-community connectors"
            },
            {
                "question": "What is the largest community?",
                "description": "Find the community with most members"
            },
            {
                "question": "Show connections between different communities",
                "description": "Analyze inter-community relationships"
            },
            {
                "question": "Who has the most followers?",
                "description": "Find most connected users"
            },
            {
                "question": "Find isolated users with no connections",
                "description": "Identify disconnected users"
            },
            {
                "question": "Show users in community X",
                "description": "List members of a specific community"
            }
        ],
        "llm_available": nlq_service.is_available()
    }


@router.post("/validate")
async def validate_cypher(cypher: str):
    """Validate a Cypher query without executing it."""
    try:
        # Try to explain the query (won't execute, just validates)
        neo4j_service.execute_query(f"EXPLAIN {cypher}")
        return {"valid": True, "message": "Query is valid"}
    except Exception as e:
        return {"valid": False, "message": str(e)}
