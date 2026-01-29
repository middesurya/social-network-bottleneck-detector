"""User endpoints."""
from fastapi import APIRouter, HTTPException, Query

from app.services.neo4j_service import neo4j_service
from app.schemas.responses import UserResponse, UsersListResponse

router = APIRouter()


@router.get("/", response_model=UsersListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max users to return"),
    order_by: str = Query("follower_count", description="Field to order by"),
    descending: bool = Query(True, description="Sort descending"),
):
    """Get paginated list of users."""
    users = neo4j_service.get_users(
        skip=skip,
        limit=limit,
        order_by=order_by,
        descending=descending
    )
    
    # Get total count
    stats = neo4j_service.get_graph_stats()
    total = stats.get("user_count", len(users))
    
    return UsersListResponse(
        users=[UserResponse(**u) for u in users],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get a specific user by ID."""
    user = neo4j_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user)


@router.get("/{user_id}/connections")
async def get_user_connections(user_id: str):
    """Get a user's followers and following lists."""
    user = neo4j_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    connections = neo4j_service.get_user_connections(user_id)
    return {
        "user_id": user_id,
        "followers": connections["followers"],
        "following": connections["following"],
        "follower_count": len(connections["followers"]),
        "following_count": len(connections["following"])
    }


@router.get("/{user_id}/ego-network")
async def get_ego_network(
    user_id: str,
    depth: int = Query(1, ge=1, le=3, description="Depth of ego network"),
):
    """Get the ego network around a user."""
    user = neo4j_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = """
    MATCH path = (center:User {id: $user_id})-[:FOLLOWS*1..$depth]-(connected:User)
    WITH center, connected, path
    UNWIND relationships(path) as rel
    WITH center, connected, collect(DISTINCT rel) as rels
    RETURN 
        collect(DISTINCT connected {.*}) as nodes,
        size(collect(DISTINCT connected)) as node_count
    """
    results = neo4j_service.execute_query(
        query, 
        {"user_id": user_id, "depth": depth}
    )
    
    if results:
        return {
            "center": user,
            "nodes": results[0]["nodes"],
            "node_count": results[0]["node_count"],
            "depth": depth
        }
    return {"center": user, "nodes": [], "node_count": 0, "depth": depth}
