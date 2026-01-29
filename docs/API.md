# API Documentation

## Overview

The Social Network Bottleneck Detector API provides endpoints for graph analysis, bottleneck detection, and natural language queries.

**Base URL:** `http://localhost:8000/api/v1`

## Authentication

Currently, the API does not require authentication. In production, implement API key or OAuth2 authentication.

## Endpoints

### Health Check

#### `GET /health`
Check API and service health.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "neo4j": "healthy"
  }
}
```

---

### Users

#### `GET /api/v1/users`
Get paginated list of users.

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| skip | int | 0 | Number of users to skip |
| limit | int | 100 | Max users to return (1-1000) |
| order_by | string | follower_count | Field to order by |
| descending | bool | true | Sort descending |

**Response:**
```json
{
  "users": [
    {
      "id": "user_1",
      "username": "alice",
      "display_name": "Alice Johnson",
      "follower_count": 1500,
      "following_count": 300,
      "bottleneck_score": 0.75,
      "community_id": "community_a",
      "is_bottleneck": true
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 100
}
```

#### `GET /api/v1/users/{user_id}`
Get a specific user by ID.

#### `GET /api/v1/users/{user_id}/connections`
Get a user's followers and following lists.

#### `GET /api/v1/users/{user_id}/ego-network`
Get the ego network around a user.

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| depth | int | 1 | Depth of ego network (1-3) |

---

### Graph

#### `GET /api/v1/graph/stats`
Get overall graph statistics.

**Response:**
```json
{
  "user_count": 1000,
  "follows_count": 5000,
  "community_count": 5,
  "tweet_count": 0
}
```

#### `GET /api/v1/graph/subgraph`
Get a subgraph in Cytoscape.js format.

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| center_id | string | null | Center node ID for ego network |
| community_id | string | null | Filter by community |
| limit | int | 100 | Max nodes to return (1-500) |
| include_bottlenecks | bool | true | Highlight bottleneck nodes |
| min_degree | int | 0 | Minimum node degree |

**Response:**
```json
{
  "nodes": [
    {
      "data": {
        "id": "user_1",
        "label": "alice",
        "bottleneck_score": 0.75
      },
      "classes": "bottleneck community-a"
    }
  ],
  "edges": [
    {
      "data": {
        "id": "user_1-user_2",
        "source": "user_1",
        "target": "user_2",
        "type": "FOLLOWS"
      }
    }
  ],
  "metadata": {
    "node_count": 50,
    "edge_count": 120
  }
}
```

---

### Algorithms

#### `GET /api/v1/algorithms`
List available algorithms.

#### `POST /api/v1/algorithms/run/{algorithm_name}`
Run a graph algorithm.

**Available Algorithms:**
- `pagerank` - Calculate PageRank scores
- `betweenness` - Calculate betweenness centrality
- `louvain` - Detect communities using Louvain method
- `bottleneck` - Calculate composite bottleneck scores
- `degree` - Calculate degree centrality

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| write_property | bool | true | Write results to node properties |
| sample_size | int | null | Sample size for approximate algorithms |

**Response:**
```json
{
  "algorithm": "pagerank",
  "status": "completed",
  "execution_time_ms": 1234.5,
  "nodes_processed": 1000,
  "results_summary": {
    "avg_score": 0.001,
    "max_score": 0.15
  },
  "message": "PageRank scores calculated and stored"
}
```

---

### Bottlenecks

#### `GET /api/v1/bottlenecks`
Get top bottleneck nodes.

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| limit | int | 20 | Number of bottlenecks to return |
| min_score | float | 0.0 | Minimum bottleneck score (0-1) |
| community_id | string | null | Filter by community |

**Response:**
```json
{
  "bottlenecks": [
    {
      "user": { "id": "user_1", "username": "alice", ... },
      "bottleneck_score": 0.85,
      "betweenness_centrality": 0.12,
      "bridge_score": 0.9,
      "connected_communities": ["community_a", "community_b"],
      "influence_radius": 150
    }
  ],
  "total": 15
}
```

#### `GET /api/v1/bottlenecks/summary`
Get bottleneck analysis summary.

#### `GET /api/v1/bottlenecks/bridges`
Get users that bridge multiple communities.

#### `GET /api/v1/bottlenecks/{user_id}/impact`
Analyze the impact of removing a bottleneck node.

---

### Communities

#### `GET /api/v1/communities`
Get all detected communities.

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| limit | int | 50 | Max communities to return |
| min_size | int | 1 | Minimum community size |

#### `GET /api/v1/communities/{community_id}`
Get details of a specific community.

#### `GET /api/v1/communities/{community_id}/bottlenecks`
Get bottleneck nodes within a community.

#### `GET /api/v1/communities/connections/matrix`
Get inter-community connection matrix.

---

### Natural Language Queries

#### `POST /api/v1/nlq/query`
Execute a natural language query.

**Request Body:**
```json
{
  "query": "Who are the most influential users?",
  "max_results": 10
}
```

**Response:**
```json
{
  "query": "Who are the most influential users?",
  "generated_cypher": "MATCH (u:User) RETURN u ORDER BY u.pagerank DESC LIMIT $limit",
  "results": [...],
  "explanation": "Find users with highest PageRank scores",
  "confidence": 0.9
}
```

#### `GET /api/v1/nlq/examples`
Get example natural language queries.

---

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message here"
}
```

**Common Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

Currently no rate limiting is implemented. In production, consider implementing rate limits.

## Pagination

List endpoints support pagination with `skip` and `limit` parameters. Responses include `total` for calculating pages.
