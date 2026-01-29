"""Neo4j database service for graph operations."""
import logging
from typing import Any, Optional
from contextlib import contextmanager

from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, AuthError

from app.config import settings

logger = logging.getLogger(__name__)


class Neo4jService:
    """Service class for Neo4j database operations."""
    
    def __init__(self):
        """Initialize Neo4j driver."""
        self._driver: Optional[Driver] = None
    
    @property
    def driver(self) -> Driver:
        """Get or create Neo4j driver."""
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password)
            )
        return self._driver
    
    def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j driver closed")
    
    def verify_connectivity(self) -> bool:
        """Verify Neo4j connection is working."""
        try:
            self.driver.verify_connectivity()
            return True
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Neo4j connectivity check failed: {e}")
            raise
    
    @contextmanager
    def get_session(self, database: Optional[str] = None) -> Session:
        """Get a Neo4j session context manager."""
        db = database or settings.neo4j_database
        session = self.driver.session(database=db)
        try:
            yield session
        finally:
            session.close()
    
    def execute_query(
        self,
        query: str,
        parameters: Optional[dict] = None,
        database: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query and return results as list of dicts."""
        with self.get_session(database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_write(
        self,
        query: str,
        parameters: Optional[dict] = None,
        database: Optional[str] = None
    ) -> dict[str, Any]:
        """Execute a write query and return summary."""
        with self.get_session(database) as session:
            result = session.run(query, parameters or {})
            summary = result.consume()
            return {
                "nodes_created": summary.counters.nodes_created,
                "nodes_deleted": summary.counters.nodes_deleted,
                "relationships_created": summary.counters.relationships_created,
                "relationships_deleted": summary.counters.relationships_deleted,
                "properties_set": summary.counters.properties_set,
            }
    
    # User operations
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get a user by their ID."""
        query = """
        MATCH (u:User {id: $user_id})
        RETURN u {.*} as user
        """
        results = self.execute_query(query, {"user_id": user_id})
        return results[0]["user"] if results else None
    
    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "follower_count",
        descending: bool = True
    ) -> list[dict]:
        """Get paginated list of users."""
        order = "DESC" if descending else "ASC"
        query = f"""
        MATCH (u:User)
        RETURN u {{.*}} as user
        ORDER BY u.{order_by} {order}
        SKIP $skip
        LIMIT $limit
        """
        results = self.execute_query(query, {"skip": skip, "limit": limit})
        return [r["user"] for r in results]
    
    def get_user_connections(self, user_id: str) -> dict:
        """Get a user's followers and following."""
        query = """
        MATCH (u:User {id: $user_id})
        OPTIONAL MATCH (u)-[:FOLLOWS]->(following:User)
        OPTIONAL MATCH (follower:User)-[:FOLLOWS]->(u)
        RETURN 
            collect(DISTINCT following {.*}) as following,
            collect(DISTINCT follower {.*}) as followers
        """
        results = self.execute_query(query, {"user_id": user_id})
        if results:
            return results[0]
        return {"following": [], "followers": []}
    
    # Graph statistics
    def get_graph_stats(self) -> dict:
        """Get overall graph statistics."""
        try:
            # Get user count
            user_result = self.execute_query("MATCH (u:User) RETURN count(u) as cnt")
            user_count = user_result[0]["cnt"] if user_result else 0
            
            # Get relationship count
            rel_result = self.execute_query("MATCH ()-[r:FOLLOWS]->() RETURN count(r) as cnt")
            follows_count = rel_result[0]["cnt"] if rel_result else 0
            
            # Get community count
            comm_result = self.execute_query("MATCH (u:User) WHERE u.community_id IS NOT NULL RETURN count(DISTINCT u.community_id) as cnt")
            community_count = comm_result[0]["cnt"] if comm_result else 0
            
            # Get bottleneck count
            bn_result = self.execute_query("MATCH (u:User) WHERE u.is_bottleneck = true RETURN count(u) as cnt")
            bottleneck_count = bn_result[0]["cnt"] if bn_result else 0
            
            return {
                "user_count": user_count,
                "follows_count": follows_count,
                "community_count": community_count,
                "bottleneck_count": bottleneck_count,
                "tweet_count": 0
            }
        except Exception as e:
            import logging
            logging.error(f"Error getting graph stats: {e}")
            return {"user_count": 0, "follows_count": 0, "community_count": 0, "bottleneck_count": 0}
    
    def get_top_bottlenecks(self, limit: int = 10) -> list[dict]:
        """Get top bottleneck nodes by score."""
        query = """
        MATCH (u:User)
        WHERE u.bottleneck_score IS NOT NULL
        RETURN u {.*} as user
        ORDER BY u.bottleneck_score DESC
        LIMIT $limit
        """
        results = self.execute_query(query, {"limit": limit})
        return [r["user"] for r in results]


# Singleton instance
neo4j_service = Neo4jService()
