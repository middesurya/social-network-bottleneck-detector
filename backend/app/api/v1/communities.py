"""Community endpoints."""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from app.services.neo4j_service import neo4j_service
from app.schemas.responses import CommunityResponse, UserResponse

router = APIRouter()


@router.get("/")
async def get_communities(
    limit: int = Query(50, ge=1, le=200, description="Max communities to return"),
    min_size: int = Query(1, ge=1, description="Minimum community size"),
):
    """Get all detected communities."""
    query = """
    MATCH (u:User)
    WHERE u.community_id IS NOT NULL
    WITH u.community_id as communityId, collect(u) as members
    WHERE size(members) >= $min_size
    
    // Get community stats
    WITH communityId, members, size(members) as memberCount
    
    // Count internal vs external edges
    UNWIND members as m
    OPTIONAL MATCH (m)-[r:FOLLOWS]-(other:User)
    WITH communityId, memberCount, members,
         sum(CASE WHEN other.community_id = communityId THEN 1 ELSE 0 END) as internalEdges,
         sum(CASE WHEN other.community_id <> communityId THEN 1 ELSE 0 END) as externalEdges
    
    // Get top members by bottleneck score
    UNWIND members as m
    WITH communityId, memberCount, internalEdges, externalEdges, m
    ORDER BY m.bottleneck_score DESC
    WITH communityId, memberCount, internalEdges, externalEdges, 
         collect(m {.*})[0..5] as topMembers
    
    RETURN {
        id: communityId,
        member_count: memberCount,
        internal_edges: internalEdges,
        external_edges: externalEdges,
        internal_density: toFloat(internalEdges) / (memberCount * (memberCount - 1) + 1),
        top_members: topMembers
    } as community
    ORDER BY memberCount DESC
    LIMIT $limit
    """
    results = neo4j_service.execute_query(query, {
        "limit": limit,
        "min_size": min_size
    })
    
    communities = []
    for r in results:
        c = r["community"]
        communities.append({
            "id": c["id"],
            "member_count": c["member_count"],
            "internal_edges": c["internal_edges"],
            "external_edges": c["external_edges"],
            "internal_density": c["internal_density"],
            "top_members": [
                UserResponse(
                    id=m["id"],
                    username=m.get("username", m["id"]),
                    display_name=m.get("display_name"),
                    follower_count=m.get("follower_count", 0),
                    following_count=m.get("following_count", 0),
                    bottleneck_score=m.get("bottleneck_score"),
                    community_id=m.get("community_id")
                ) for m in c["top_members"]
            ]
        })
    
    return {
        "communities": communities,
        "total": len(communities)
    }


@router.get("/{community_id}")
async def get_community(community_id: str):
    """Get details of a specific community."""
    query = """
    MATCH (u:User {community_id: $community_id})
    WITH collect(u) as members
    
    // Calculate stats
    WITH members, size(members) as memberCount
    
    UNWIND members as m
    OPTIONAL MATCH (m)-[:FOLLOWS]-(other:User)
    WITH members, memberCount,
         sum(CASE WHEN other.community_id = $community_id THEN 1 ELSE 0 END) as internalEdges,
         sum(CASE WHEN other.community_id <> $community_id AND other.community_id IS NOT NULL THEN 1 ELSE 0 END) as externalEdges,
         collect(DISTINCT other.community_id) as connectedCommunities
    
    // Get all members sorted by bottleneck score
    UNWIND members as m
    WITH memberCount, internalEdges, externalEdges, 
         [c IN connectedCommunities WHERE c IS NOT NULL AND c <> $community_id] as connectedCommunities,
         m
    ORDER BY m.bottleneck_score DESC
    
    RETURN {
        id: $community_id,
        member_count: memberCount,
        internal_edges: internalEdges,
        external_edges: externalEdges,
        connected_communities: connectedCommunities,
        members: collect(m {.*})
    } as community
    """
    results = neo4j_service.execute_query(query, {"community_id": community_id})
    
    if not results or not results[0]["community"]["members"]:
        raise HTTPException(status_code=404, detail="Community not found")
    
    c = results[0]["community"]
    return {
        "id": c["id"],
        "member_count": c["member_count"],
        "internal_edges": c["internal_edges"],
        "external_edges": c["external_edges"],
        "connected_communities": c["connected_communities"],
        "members": [
            UserResponse(
                id=m["id"],
                username=m.get("username", m["id"]),
                display_name=m.get("display_name"),
                follower_count=m.get("follower_count", 0),
                following_count=m.get("following_count", 0),
                bottleneck_score=m.get("bottleneck_score"),
                community_id=m.get("community_id")
            ) for m in c["members"]
        ]
    }


@router.get("/{community_id}/bottlenecks")
async def get_community_bottlenecks(
    community_id: str,
    limit: int = Query(10, ge=1, le=50),
):
    """Get bottleneck nodes within a specific community."""
    query = """
    MATCH (u:User {community_id: $community_id})
    WHERE u.bottleneck_score IS NOT NULL
    
    OPTIONAL MATCH (u)-[:FOLLOWS]-(neighbor:User)
    WHERE neighbor.community_id <> $community_id
    WITH u, collect(DISTINCT neighbor.community_id) as bridgedCommunities
    
    RETURN u {
        .*,
        bridged_communities: bridgedCommunities
    } as bottleneck
    ORDER BY u.bottleneck_score DESC
    LIMIT $limit
    """
    results = neo4j_service.execute_query(query, {
        "community_id": community_id,
        "limit": limit
    })
    
    return {
        "community_id": community_id,
        "bottlenecks": [r["bottleneck"] for r in results],
        "total": len(results)
    }


@router.get("/connections/matrix")
async def get_community_connection_matrix():
    """Get a matrix of connections between communities."""
    query = """
    MATCH (u1:User)-[:FOLLOWS]->(u2:User)
    WHERE u1.community_id IS NOT NULL AND u2.community_id IS NOT NULL
      AND u1.community_id <> u2.community_id
    WITH u1.community_id as source, u2.community_id as target, count(*) as weight
    RETURN source, target, weight
    ORDER BY weight DESC
    """
    results = neo4j_service.execute_query(query)
    
    # Build matrix representation
    communities = set()
    edges = []
    for r in results:
        communities.add(r["source"])
        communities.add(r["target"])
        edges.append({
            "source": r["source"],
            "target": r["target"],
            "weight": r["weight"]
        })
    
    return {
        "communities": list(communities),
        "connections": edges,
        "total_inter_community_edges": sum(e["weight"] for e in edges)
    }
