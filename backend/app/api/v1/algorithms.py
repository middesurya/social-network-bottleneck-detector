"""Algorithm execution endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Optional
import time

from app.services.neo4j_service import neo4j_service
from app.schemas.responses import AlgorithmRunResponse

router = APIRouter()


AVAILABLE_ALGORITHMS = {
    "pagerank": "PageRank centrality",
    "betweenness": "Betweenness centrality", 
    "louvain": "Louvain community detection",
    "bottleneck": "Composite bottleneck score calculation",
    "degree": "Degree centrality",
}


@router.get("/")
async def list_algorithms():
    """List available algorithms."""
    return {
        "algorithms": AVAILABLE_ALGORITHMS,
        "note": "Use POST /algorithms/run/{name} to execute"
    }


@router.post("/run/{algorithm_name}", response_model=AlgorithmRunResponse)
async def run_algorithm(
    algorithm_name: str,
    write_property: bool = True,
    sample_size: Optional[int] = None,
):
    """
    Run a graph algorithm.
    
    - **pagerank**: Calculate PageRank scores
    - **betweenness**: Calculate betweenness centrality
    - **louvain**: Detect communities using Louvain method
    - **bottleneck**: Calculate composite bottleneck scores
    - **degree**: Calculate degree centrality
    """
    if algorithm_name not in AVAILABLE_ALGORITHMS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown algorithm: {algorithm_name}. Available: {list(AVAILABLE_ALGORITHMS.keys())}"
        )
    
    start_time = time.time()
    
    try:
        if algorithm_name == "pagerank":
            result = await _run_pagerank(write_property)
        elif algorithm_name == "betweenness":
            result = await _run_betweenness(write_property, sample_size)
        elif algorithm_name == "louvain":
            result = await _run_louvain(write_property)
        elif algorithm_name == "bottleneck":
            result = await _run_bottleneck_score(write_property)
        elif algorithm_name == "degree":
            result = await _run_degree(write_property)
        else:
            raise HTTPException(status_code=400, detail="Algorithm not implemented")
        
        execution_time = (time.time() - start_time) * 1000
        
        return AlgorithmRunResponse(
            algorithm=algorithm_name,
            status="completed",
            execution_time_ms=round(execution_time, 2),
            nodes_processed=result.get("nodes_processed", 0),
            results_summary=result.get("summary", {}),
            message=result.get("message")
        )
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return AlgorithmRunResponse(
            algorithm=algorithm_name,
            status="failed",
            execution_time_ms=round(execution_time, 2),
            nodes_processed=0,
            results_summary={},
            message=str(e)
        )


async def _run_pagerank(write_property: bool) -> dict:
    """Run PageRank using GDS library."""
    # Check if GDS is available, fallback to manual calculation
    try:
        # Try GDS version first
        query = """
        CALL gds.pageRank.stream('social-graph')
        YIELD nodeId, score
        WITH gds.util.asNode(nodeId) AS node, score
        SET node.pagerank = score
        RETURN count(*) as nodesProcessed, avg(score) as avgScore, max(score) as maxScore
        """
        results = neo4j_service.execute_query(query)
    except Exception:
        # Fallback: Simple iterative PageRank
        query = """
        MATCH (u:User)
        WITH count(u) as totalNodes
        MATCH (u:User)
        SET u.pagerank = 1.0 / totalNodes
        WITH count(u) as initialized
        
        // Run 20 iterations
        UNWIND range(1, 20) as iteration
        MATCH (u:User)
        OPTIONAL MATCH (u)<-[:FOLLOWS]-(follower:User)
        WITH u, COALESCE(sum(follower.pagerank / CASE WHEN follower.following_count > 0 THEN follower.following_count ELSE 1 END), 0) as incomingRank
        SET u.pagerank = 0.15 + 0.85 * incomingRank
        
        WITH count(*) as updated
        MATCH (u:User)
        RETURN count(u) as nodesProcessed, avg(u.pagerank) as avgScore, max(u.pagerank) as maxScore
        """
        results = neo4j_service.execute_query(query)
    
    if results:
        return {
            "nodes_processed": results[0].get("nodesProcessed", 0),
            "summary": {
                "avg_score": results[0].get("avgScore"),
                "max_score": results[0].get("maxScore")
            },
            "message": "PageRank scores calculated and stored"
        }
    return {"nodes_processed": 0, "message": "No nodes processed"}


async def _run_betweenness(write_property: bool, sample_size: Optional[int]) -> dict:
    """Run betweenness centrality calculation."""
    # Approximate betweenness using OPTIONAL MATCH counting
    query = """
    MATCH (u:User)
    OPTIONAL MATCH (u)-[outRel:FOLLOWS]->()
    OPTIONAL MATCH (u)<-[inRel:FOLLOWS]-()
    WITH u, count(DISTINCT outRel) as outDegree, count(DISTINCT inRel) as inDegree
    WITH u, outDegree + inDegree as degree, outDegree, inDegree
    WITH u, degree,
         CASE WHEN degree > 0 THEN 
             toFloat(outDegree * inDegree) / (degree * degree)
         ELSE 0.0 END as approxBetweenness
    SET u.betweenness_centrality = approxBetweenness
    RETURN count(u) as nodesProcessed, 
           avg(approxBetweenness) as avgScore, 
           max(approxBetweenness) as maxScore
    """
    results = neo4j_service.execute_query(query)
    
    if results:
        return {
            "nodes_processed": results[0].get("nodesProcessed", 0),
            "summary": {
                "avg_score": results[0].get("avgScore"),
                "max_score": results[0].get("maxScore")
            },
            "message": "Betweenness centrality approximated and stored"
        }
    return {"nodes_processed": 0, "message": "No nodes processed"}


async def _run_louvain(write_property: bool) -> dict:
    """Run Louvain community detection."""
    # Simple label propagation as fallback
    query = """
    // Initialize: each node is its own community
    MATCH (u:User)
    SET u.community_id = u.id
    WITH count(u) as initialized
    
    // Run label propagation iterations
    UNWIND range(1, 10) as iteration
    MATCH (u:User)-[:FOLLOWS]-(neighbor:User)
    WITH u, neighbor.community_id as neighborCommunity, count(*) as weight
    ORDER BY weight DESC
    WITH u, collect(neighborCommunity)[0] as dominantCommunity
    SET u.community_id = dominantCommunity
    
    WITH count(*) as updated
    MATCH (u:User)
    WITH u.community_id as communityId, count(u) as memberCount
    RETURN count(DISTINCT communityId) as communitiesFound, 
           avg(memberCount) as avgCommunitySize,
           max(memberCount) as maxCommunitySize
    """
    results = neo4j_service.execute_query(query)
    
    if results:
        return {
            "nodes_processed": results[0].get("communitiesFound", 0),
            "summary": {
                "communities_found": results[0].get("communitiesFound"),
                "avg_community_size": results[0].get("avgCommunitySize"),
                "max_community_size": results[0].get("maxCommunitySize")
            },
            "message": "Community detection completed"
        }
    return {"nodes_processed": 0, "message": "No communities detected"}


async def _run_bottleneck_score(write_property: bool) -> dict:
    """Calculate composite bottleneck score."""
    query = """
    MATCH (u:User)
    WHERE u.pagerank IS NOT NULL AND u.betweenness_centrality IS NOT NULL
    
    // Calculate bridge score: users connected to multiple communities
    OPTIONAL MATCH (u)-[:FOLLOWS]-(neighbor:User)
    WHERE neighbor.community_id IS NOT NULL AND neighbor.community_id <> u.community_id
    WITH u, count(DISTINCT neighbor.community_id) as bridgedCommunities
    
    // Normalize scores and calculate composite
    WITH u, bridgedCommunities,
         COALESCE(u.betweenness_centrality, 0) as betweenness,
         COALESCE(u.pagerank, 0) as pagerank
    
    // Get max values for normalization
    MATCH (all:User)
    WITH u, bridgedCommunities, betweenness, pagerank,
         max(all.betweenness_centrality) as maxBetweenness,
         max(all.pagerank) as maxPagerank,
         max(5) as maxBridged  // Cap at 5 communities
    
    WITH u,
         CASE WHEN maxBetweenness > 0 THEN betweenness / maxBetweenness ELSE 0 END as normBetweenness,
         CASE WHEN maxPagerank > 0 THEN pagerank / maxPagerank ELSE 0 END as normPagerank,
         toFloat(bridgedCommunities) / maxBridged as bridgeScore
    
    // Composite score: 40% betweenness + 30% pagerank + 30% bridge
    SET u.bridge_score = bridgeScore,
        u.bottleneck_score = (0.4 * normBetweenness) + (0.3 * normPagerank) + (0.3 * bridgeScore),
        u.is_bottleneck = CASE WHEN (0.4 * normBetweenness) + (0.3 * normPagerank) + (0.3 * bridgeScore) > 0.5 THEN true ELSE false END
    
    RETURN count(u) as nodesProcessed,
           avg(u.bottleneck_score) as avgScore,
           sum(CASE WHEN u.is_bottleneck THEN 1 ELSE 0 END) as bottleneckCount
    """
    results = neo4j_service.execute_query(query)
    
    if results:
        return {
            "nodes_processed": results[0].get("nodesProcessed", 0),
            "summary": {
                "avg_bottleneck_score": results[0].get("avgScore"),
                "bottleneck_count": results[0].get("bottleneckCount")
            },
            "message": "Bottleneck scores calculated"
        }
    return {"nodes_processed": 0, "message": "Run pagerank and betweenness first"}


async def _run_degree(write_property: bool) -> dict:
    """Calculate degree centrality."""
    query = """
    MATCH (u:User)
    OPTIONAL MATCH (u)-[outRel:FOLLOWS]->()
    OPTIONAL MATCH (u)<-[inRel:FOLLOWS]-()
    WITH u, count(DISTINCT outRel) as outDegree, count(DISTINCT inRel) as inDegree
    SET u.out_degree = outDegree,
        u.in_degree = inDegree,
        u.degree_centrality = toFloat(outDegree + inDegree)
    RETURN count(u) as nodesProcessed,
           avg(u.degree_centrality) as avgDegree,
           max(u.degree_centrality) as maxDegree
    """
    results = neo4j_service.execute_query(query)
    
    if results:
        return {
            "nodes_processed": results[0].get("nodesProcessed", 0),
            "summary": {
                "avg_degree": results[0].get("avgDegree"),
                "max_degree": results[0].get("maxDegree")
            },
            "message": "Degree centrality calculated"
        }
    return {"nodes_processed": 0, "message": "No nodes processed"}
