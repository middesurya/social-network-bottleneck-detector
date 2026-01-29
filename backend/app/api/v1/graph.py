"""Graph endpoints for visualization."""
from fastapi import APIRouter, Query
from typing import Optional

from app.services.neo4j_service import neo4j_service
from app.schemas.responses import SubgraphResponse, GraphStatsResponse, CytoscapeNode, CytoscapeEdge

router = APIRouter()


@router.get("/stats")
async def get_graph_stats():
    """Get overall graph statistics."""
    stats = neo4j_service.get_graph_stats()
    return stats


@router.get("/subgraph", response_model=SubgraphResponse)
async def get_subgraph(
    center_id: Optional[str] = Query(None, description="Center node ID for ego network"),
    community_id: Optional[str] = Query(None, description="Filter by community"),
    limit: int = Query(100, ge=1, le=500, description="Max nodes to return"),
    include_bottlenecks: bool = Query(True, description="Highlight bottleneck nodes"),
    min_degree: int = Query(0, ge=0, description="Minimum node degree"),
):
    """
    Get a subgraph in Cytoscape.js format.
    
    Can filter by:
    - center_id: Get ego network around a specific user
    - community_id: Get all nodes in a community
    - min_degree: Filter by minimum connections
    """
    # Build query based on filters
    if center_id:
        query = """
        MATCH (center:User {id: $center_id})
        CALL {
            WITH center
            MATCH (center)-[:FOLLOWS]-(neighbor:User)
            RETURN neighbor
            LIMIT $limit
        }
        WITH center, collect(neighbor) + [center] as nodes
        UNWIND nodes as n
        WITH collect(DISTINCT n) as allNodes
        UNWIND allNodes as source
        UNWIND allNodes as target
        OPTIONAL MATCH (source)-[r:FOLLOWS]->(target)
        WHERE source <> target AND r IS NOT NULL
        RETURN 
            collect(DISTINCT source {.*, labels: labels(source)}) as nodes,
            collect(DISTINCT {source: source.id, target: target.id, type: type(r)}) as edges
        """
        params = {"center_id": center_id, "limit": limit}
    elif community_id:
        query = """
        MATCH (n:User {community_id: $community_id})
        WITH n LIMIT $limit
        WITH collect(n) as nodes
        UNWIND nodes as source
        UNWIND nodes as target
        OPTIONAL MATCH (source)-[r:FOLLOWS]->(target)
        WHERE source <> target AND r IS NOT NULL
        RETURN 
            collect(DISTINCT source {.*, labels: labels(source)}) as nodes,
            collect(DISTINCT {source: source.id, target: target.id, type: type(r)}) as edges
        """
        params = {"community_id": community_id, "limit": limit}
    else:
        # Get top nodes by bottleneck score or followers
        query = """
        MATCH (n:User)
        WHERE n.follower_count >= $min_degree OR n.following_count >= $min_degree
        WITH n
        ORDER BY COALESCE(n.bottleneck_score, 0) DESC, n.follower_count DESC
        LIMIT $limit
        WITH collect(n) as nodes
        UNWIND nodes as source
        UNWIND nodes as target
        OPTIONAL MATCH (source)-[r:FOLLOWS]->(target)
        WHERE source <> target AND r IS NOT NULL
        RETURN 
            collect(DISTINCT source {.*, labels: labels(source)}) as nodes,
            collect(DISTINCT {source: source.id, target: target.id, type: type(r)}) as edges
        """
        params = {"limit": limit, "min_degree": min_degree}
    
    results = neo4j_service.execute_query(query, params)
    
    if not results:
        return SubgraphResponse(nodes=[], edges=[], metadata={})
    
    data = results[0]
    nodes_data = data.get("nodes", [])
    edges_data = data.get("edges", [])
    
    # Convert to Cytoscape format
    cytoscape_nodes = []
    for node in nodes_data:
        if node:
            node_classes = []
            if node.get("is_bottleneck"):
                node_classes.append("bottleneck")
            if node.get("community_id"):
                node_classes.append(f"community-{node['community_id']}")
            
            cytoscape_nodes.append(CytoscapeNode(
                data={
                    "id": node["id"],
                    "label": node.get("username", node["id"]),
                    **{k: v for k, v in node.items() if k not in ["labels"]}
                },
                classes=" ".join(node_classes) if node_classes else None
            ))
    
    cytoscape_edges = []
    for edge in edges_data:
        if edge and edge.get("source") and edge.get("target"):
            cytoscape_edges.append(CytoscapeEdge(
                data={
                    "id": f"{edge['source']}-{edge['target']}",
                    "source": edge["source"],
                    "target": edge["target"],
                    "type": edge.get("type", "FOLLOWS")
                }
            ))
    
    return SubgraphResponse(
        nodes=cytoscape_nodes,
        edges=cytoscape_edges,
        metadata={
            "node_count": len(cytoscape_nodes),
            "edge_count": len(cytoscape_edges),
            "filters": {
                "center_id": center_id,
                "community_id": community_id,
                "limit": limit,
                "min_degree": min_degree
            }
        }
    )


@router.get("/communities-overview")
async def get_communities_overview():
    """Get overview of all communities and their connections."""
    query = """
    MATCH (u:User)
    WHERE u.community_id IS NOT NULL
    WITH u.community_id as communityId, collect(u) as members
    RETURN communityId, 
           size(members) as memberCount,
           avg(COALESCE(members[0].bottleneck_score, 0)) as avgBottleneckScore
    ORDER BY memberCount DESC
    """
    results = neo4j_service.execute_query(query)
    
    return {
        "communities": results,
        "total_communities": len(results)
    }
