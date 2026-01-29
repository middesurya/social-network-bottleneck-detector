"""Natural Language Query service using LangChain and OpenAI."""
import logging
from typing import Optional, Tuple
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings

logger = logging.getLogger(__name__)

# Neo4j schema description for the LLM
SCHEMA_DESCRIPTION = """
Neo4j Database Schema:

Nodes:
- User: id (STRING), username (STRING), display_name (STRING), follower_count (INTEGER), 
  following_count (INTEGER), betweenness_centrality (FLOAT), pagerank (FLOAT), 
  community_id (STRING), bottleneck_score (FLOAT), is_bottleneck (BOOLEAN), 
  bridge_score (FLOAT), in_degree (INTEGER), out_degree (INTEGER)

Relationships:
- (User)-[:FOLLOWS]->(User)

Key Metrics:
- bottleneck_score: Composite score (0-2) indicating how critical a user is for network connectivity
- betweenness_centrality: How many shortest paths pass through this user (0-1)
- pagerank: Influence score based on follower quality
- bridge_score: Number of different communities this user connects
- community_id: The community this user belongs to
- is_bottleneck: Boolean flag for high bottleneck score users
"""

CYPHER_GENERATION_PROMPT = """You are a Neo4j Cypher expert. Given the schema below and a natural language question, 
generate a valid Cypher query to answer the question.

{schema}

Rules:
1. Only use node labels, relationship types, and properties that exist in the schema
2. Always include LIMIT clause (default 10 if not specified)
3. Return useful properties, not just node references
4. For bottleneck queries, order by bottleneck_score DESC
5. For influence queries, order by pagerank DESC
6. Use OPTIONAL MATCH for relationships that might not exist
7. Do NOT use size() on pattern expressions - use count() with OPTIONAL MATCH instead

Question: {question}

Return ONLY the Cypher query, no explanations or markdown:"""


class NLQService:
    """Service for converting natural language to Cypher queries."""
    
    def __init__(self):
        self._llm = None
        self._chain = None
    
    @property
    def llm(self) -> ChatOpenAI:
        """Lazy load the LLM."""
        if self._llm is None:
            api_key = settings.openai_api_key
            if not api_key:
                raise ValueError("OPENAI_API_KEY not configured")
            
            self._llm = ChatOpenAI(
                model="gpt-4o-mini",  # Cost-effective, fast, good for Cypher
                temperature=0,
                api_key=api_key
            )
        return self._llm
    
    @property
    def chain(self):
        """Create the LangChain chain for Cypher generation."""
        if self._chain is None:
            prompt = ChatPromptTemplate.from_template(CYPHER_GENERATION_PROMPT)
            self._chain = prompt | self.llm | StrOutputParser()
        return self._chain
    
    def generate_cypher(self, question: str) -> Tuple[str, float]:
        """
        Generate a Cypher query from a natural language question.
        
        Returns:
            Tuple of (cypher_query, confidence_score)
        """
        try:
            # Generate Cypher using LangChain
            cypher = self.chain.invoke({
                "schema": SCHEMA_DESCRIPTION,
                "question": question
            })
            
            # Clean up the response
            cypher = cypher.strip()
            if cypher.startswith("```"):
                cypher = cypher.split("```")[1]
                if cypher.startswith("cypher"):
                    cypher = cypher[6:]
                cypher = cypher.strip()
            
            # Basic validation
            if not cypher.upper().startswith(("MATCH", "OPTIONAL", "CALL", "WITH")):
                logger.warning(f"Generated query doesn't start with expected keyword: {cypher[:50]}")
                return None, 0.0
            
            logger.info(f"Generated Cypher for '{question}': {cypher}")
            return cypher, 0.85  # GPT-4 generated queries are generally reliable
            
        except Exception as e:
            logger.error(f"Error generating Cypher: {e}")
            return None, 0.0
    
    def is_available(self) -> bool:
        """Check if the NLQ service is available (API key configured)."""
        return bool(settings.openai_api_key)


# Fallback pattern-based queries (used when LLM is not available)
QUERY_PATTERNS = {
    "most influential": {
        "cypher": "MATCH (u:User) RETURN u ORDER BY u.pagerank DESC LIMIT $limit",
        "description": "Find users with highest PageRank"
    },
    "top bottlenecks": {
        "cypher": "MATCH (u:User) WHERE u.is_bottleneck = true RETURN u ORDER BY u.bottleneck_score DESC LIMIT $limit",
        "description": "Find top bottleneck nodes"
    },
    "largest community": {
        "cypher": """
            MATCH (u:User) 
            WHERE u.community_id IS NOT NULL
            WITH u.community_id as cid, count(u) as size
            ORDER BY size DESC LIMIT 1
            MATCH (u:User {community_id: cid})
            RETURN u LIMIT $limit
        """,
        "description": "Find members of the largest community"
    },
    "bridge users": {
        "cypher": """
            MATCH (u:User)-[:FOLLOWS]-(n:User)
            WHERE u.community_id <> n.community_id
            WITH u, count(DISTINCT n.community_id) as bridged
            WHERE bridged >= 2
            RETURN u, bridged ORDER BY bridged DESC LIMIT $limit
        """,
        "description": "Find users connecting multiple communities"
    },
    "most connected": {
        "cypher": """
            MATCH (u:User)
            RETURN u ORDER BY (u.follower_count + u.following_count) DESC LIMIT $limit
        """,
        "description": "Find users with most connections"
    },
    "isolated users": {
        "cypher": """
            MATCH (u:User)
            WHERE NOT (u)-[:FOLLOWS]-()
            RETURN u LIMIT $limit
        """,
        "description": "Find users with no connections"
    },
    "community connections": {
        "cypher": """
            MATCH (u1:User)-[:FOLLOWS]->(u2:User)
            WHERE u1.community_id <> u2.community_id
            RETURN u1.community_id as from_community, u2.community_id as to_community, count(*) as connections
            ORDER BY connections DESC LIMIT $limit
        """,
        "description": "Show connections between communities"
    }
}


def match_query_pattern(query: str) -> Optional[dict]:
    """Match natural language query to known patterns (fallback)."""
    query_lower = query.lower()
    
    for pattern_key, pattern_data in QUERY_PATTERNS.items():
        if pattern_key in query_lower:
            return pattern_data
    
    # Fuzzy matching for common variations
    if any(word in query_lower for word in ["influential", "important", "powerful"]):
        return QUERY_PATTERNS["most influential"]
    
    if any(word in query_lower for word in ["bottleneck", "critical", "bridge"]):
        return QUERY_PATTERNS["top bottlenecks"]
    
    if any(word in query_lower for word in ["community", "group", "cluster"]):
        return QUERY_PATTERNS["largest community"]
    
    if any(word in query_lower for word in ["connected", "popular", "followers"]):
        return QUERY_PATTERNS["most connected"]
    
    return None


# Singleton instance
nlq_service = NLQService()
