"""Bottleneck detection endpoints."""
from fastapi import APIRouter, Query
from typing import Optional

from app.services.neo4j_service import neo4j_service
from app.schemas.responses import BottleneckResponse, UserResponse

router = APIRouter()


@router.get("/")
async def get_bottlenecks(
    limit: int = Query(20, ge=1, le=100, description="Number of bottlenecks to return"),
    min_score: float = Query(0.0, ge=0.0, le=1.0, description="Minimum bottleneck score"),
    community_id: Optional[str] = Query(None, description="Filter by community"),
):
    """Get top bottleneck nodes in the network."""
    query = """
    MATCH (u:User)
    WHERE u.bottleneck_score IS NOT NULL 
      AND u.bottleneck_score >= $min_score
      AND ($community_id IS NULL OR u.community_id = $community_id)
    
    // Get connected communities
    OPTIONAL MATCH (u)-[:FOLLOWS]-(neighbor:User)
    WHERE neighbor.community_id IS NOT NULL
    WITH u, collect(DISTINCT neighbor.community_id) as connectedCommunities
    
    // Count influence radius
    OPTIONAL MATCH (u)-[:FOLLOWS*1..2]-(influenced:User)
    WITH u, connectedCommunities, count(DISTINCT influenced) as influenceRadius
    
    RETURN u {
        .*,
        connected_communities: connectedCommunities,
        influence_radius: influenceRadius
    } as bottleneck
    ORDER BY u.bottleneck_score DESC
    LIMIT $limit
    """
    results = neo4j_service.execute_query(query, {
        "limit": limit,
        "min_score": min_score,
        "community_id": community_id
    })
    
    bottlenecks = []
    for r in results:
        b = r["bottleneck"]
        bottlenecks.append({
            "user": {
                "id": b["id"],
                "username": b.get("username", b["id"]),
                "display_name": b.get("display_name"),
                "follower_count": b.get("follower_count", 0),
                "following_count": b.get("following_count", 0),
                "betweenness_centrality": b.get("betweenness_centrality"),
                "pagerank": b.get("pagerank"),
                "bottleneck_score": b.get("bottleneck_score"),
                "community_id": b.get("community_id"),
                "is_bottleneck": b.get("is_bottleneck", False)
            },
            "bottleneck_score": b.get("bottleneck_score", 0),
            "betweenness_centrality": b.get("betweenness_centrality", 0),
            "bridge_score": b.get("bridge_score", 0),
            "connected_communities": b.get("connected_communities", []),
            "influence_radius": b.get("influence_radius", 0)
        })
    
    return {
        "bottlenecks": bottlenecks,
        "total": len(bottlenecks),
        "filters": {
            "min_score": min_score,
            "community_id": community_id
        }
    }


@router.get("/summary")
async def get_bottleneck_summary():
    """Get summary statistics about bottleneck nodes."""
    query = """
    MATCH (u:User)
    WHERE u.bottleneck_score IS NOT NULL
    WITH u
    RETURN {
        total_analyzed: count(u),
        bottleneck_count: sum(CASE WHEN u.is_bottleneck THEN 1 ELSE 0 END),
        avg_bottleneck_score: avg(u.bottleneck_score),
        max_bottleneck_score: max(u.bottleneck_score),
        min_bottleneck_score: min(u.bottleneck_score),
        score_std_dev: stDev(u.bottleneck_score)
    } as summary
    """
    results = neo4j_service.execute_query(query)
    
    if results:
        return results[0]["summary"]
    return {
        "total_analyzed": 0,
        "bottleneck_count": 0,
        "avg_bottleneck_score": None,
        "message": "No bottleneck analysis found. Run the bottleneck algorithm first."
    }


@router.get("/bridges")
async def get_community_bridges(
    limit: int = Query(20, ge=1, le=100),
):
    """Get users that bridge multiple communities."""
    query = """
    MATCH (u:User)-[:FOLLOWS]-(neighbor:User)
    WHERE u.community_id IS NOT NULL AND neighbor.community_id IS NOT NULL
      AND u.community_id <> neighbor.community_id
    WITH u, collect(DISTINCT neighbor.community_id) as bridgedCommunities
    WHERE size(bridgedCommunities) >= 2
    RETURN u {
        .*,
        bridged_communities: bridgedCommunities,
        bridge_count: size(bridgedCommunities)
    } as bridge
    ORDER BY size(bridgedCommunities) DESC, u.bottleneck_score DESC
    LIMIT $limit
    """
    results = neo4j_service.execute_query(query, {"limit": limit})
    
    return {
        "bridges": [r["bridge"] for r in results],
        "total": len(results)
    }


@router.get("/{user_id}/impact")
async def get_bottleneck_impact(user_id: str):
    """Analyze the impact of removing a bottleneck node."""
    query = """
    MATCH (u:User {id: $user_id})
    
    // Get direct connections
    OPTIONAL MATCH (u)-[:FOLLOWS]-(direct:User)
    WITH u, collect(DISTINCT direct) as directConnections
    
    // Get paths that go through this user
    OPTIONAL MATCH path = (a:User)-[:FOLLOWS*2..3]-(b:User)
    WHERE u IN nodes(path) AND a <> b AND a <> u AND b <> u
    WITH u, directConnections, count(DISTINCT path) as pathsThrough
    
    // Get community connections
    OPTIONAL MATCH (u)-[:FOLLOWS]-(neighbor:User)
    WHERE neighbor.community_id <> u.community_id
    WITH u, directConnections, pathsThrough, 
         count(DISTINCT neighbor.community_id) as communitiesConnected
    
    RETURN {
        user_id: u.id,
        username: u.username,
        bottleneck_score: u.bottleneck_score,
        direct_connections: size(directConnections),
        paths_through_node: pathsThrough,
        communities_connected: communitiesConnected,
        estimated_impact: CASE 
            WHEN pathsThrough > 100 THEN 'critical'
            WHEN pathsThrough > 50 THEN 'high'
            WHEN pathsThrough > 20 THEN 'medium'
            ELSE 'low'
        END
    } as impact
    """
    results = neo4j_service.execute_query(query, {"user_id": user_id})
    
    if results:
        return results[0]["impact"]
    return {"error": "User not found", "user_id": user_id}
