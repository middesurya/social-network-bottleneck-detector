# Architecture Documentation

## System Overview

The Social Network Bottleneck Detector is a full-stack application for analyzing social networks to identify critical "bottleneck" nodes - users who serve as bridges between different communities.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Dashboard  │  │  Explorer   │  │   Query     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│          │              │               │                       │
│          └──────────────┴───────────────┘                       │
│                         │                                       │
│              ┌──────────┴──────────┐                           │
│              │   React + Zustand   │                           │
│              │   @tanstack/query   │                           │
│              └──────────┬──────────┘                           │
└─────────────────────────┼───────────────────────────────────────┘
                          │ HTTP/REST
┌─────────────────────────┼───────────────────────────────────────┐
│                         │                                       │
│              ┌──────────┴──────────┐                           │
│              │    FastAPI Server   │                           │
│              └──────────┬──────────┘                           │
│                         │                                       │
│    ┌────────────────────┼────────────────────┐                 │
│    │                    │                    │                 │
│    ▼                    ▼                    ▼                 │
│ ┌──────────┐     ┌──────────────┐     ┌──────────┐            │
│ │  Neo4j   │     │  Algorithm   │     │  Redis   │            │
│ │ Service  │     │   Service    │     │  Cache   │            │
│ └────┬─────┘     └──────────────┘     └────┬─────┘            │
│      │                                      │                  │
│                      Backend                                   │
└──────┼──────────────────────────────────────┼──────────────────┘
       │                                      │
       ▼                                      ▼
┌──────────────┐                      ┌──────────────┐
│    Neo4j     │                      │    Redis     │
│  Graph DB    │                      │    Cache     │
└──────────────┘                      └──────────────┘
```

## Components

### Frontend (React + TypeScript)

**Technology Stack:**
- React 18 with TypeScript
- Vite for build tooling
- TailwindCSS for styling
- Zustand for state management
- @tanstack/react-query for data fetching
- Cytoscape.js for graph visualization
- react-router-dom for routing

**Key Components:**

| Component | Purpose |
|-----------|---------|
| `Layout` | Main app layout with sidebar navigation |
| `NetworkGraph` | Cytoscape.js wrapper for graph visualization |
| `GraphControls` | Zoom, pan, and layout controls |
| `NodeDetails` | Panel showing selected node information |
| `BottleneckCard` | Card displaying bottleneck user info |
| `NaturalLanguageInput` | Input for NLQ queries |

**Pages:**
- `Dashboard` - Overview metrics and quick actions
- `Explorer` - Interactive graph visualization
- `Bottlenecks` - List and filter bottleneck nodes
- `Query` - Natural language query interface

### Backend (FastAPI + Python)

**Technology Stack:**
- FastAPI for REST API
- Pydantic for data validation
- Neo4j Python driver for database
- Redis for caching
- LangChain for NLQ (optional)

**Service Layer:**

```
app/
├── api/v1/
│   ├── users.py         # User CRUD endpoints
│   ├── graph.py         # Graph/subgraph endpoints
│   ├── algorithms.py    # Algorithm execution
│   ├── bottlenecks.py   # Bottleneck analysis
│   ├── communities.py   # Community endpoints
│   └── nlq.py           # Natural language queries
├── services/
│   ├── neo4j_service.py # Neo4j connection & queries
│   └── cache_service.py # Redis caching
├── models/              # Pydantic models
├── schemas/             # API response schemas
├── config.py            # Settings management
└── main.py              # FastAPI application
```

### Database (Neo4j)

**Graph Schema:**

```cypher
// Nodes
(:User {
  id, username, display_name, bio,
  follower_count, following_count, tweet_count, verified,
  pagerank, betweenness_centrality, degree_centrality,
  bottleneck_score, bridge_score, is_bottleneck,
  community_id
})

(:Tweet {
  id, user_id, text, created_at,
  retweet_count, like_count, reply_count, quote_count
})

(:Community {
  id, name, member_count, internal_edges, external_edges
})

// Relationships
(:User)-[:FOLLOWS]->(:User)
(:User)-[:POSTED]->(:Tweet)
(:Tweet)-[:MENTIONS]->(:User)
(:User)-[:MEMBER_OF]->(:Community)
```

**Indexes:**
- User: id (unique), username (unique), follower_count, bottleneck_score, community_id, pagerank, betweenness_centrality

### Caching (Redis)

**Cache Strategy:**
- Graph stats: 5 minutes TTL
- Subgraph queries: 1 minute TTL (keyed by parameters)
- Bottleneck lists: 5 minutes TTL
- Invalidated on algorithm execution

**Key Pattern:**
```
bottleneck:{prefix}:{hash}
```

## Algorithms

### Bottleneck Score Calculation

The bottleneck score is a composite metric:

```
bottleneck_score = (w1 × normalized_betweenness) + 
                   (w2 × normalized_pagerank) + 
                   (w3 × bridge_score)
```

Default weights:
- Betweenness: 0.4
- PageRank: 0.3
- Bridge Score: 0.3

**Bridge Score:** Measures how many different communities a user connects to:
```
bridge_score = connected_communities / max_communities
```

### Algorithm Execution

1. **PageRank** - Iterative calculation of node importance based on incoming connections
2. **Betweenness Centrality** - Approximated by analyzing in/out degree ratios
3. **Louvain Community Detection** - Label propagation for community assignment
4. **Bottleneck Score** - Combines above metrics with bridge analysis

## Data Flow

### Graph Visualization Flow

```
1. User opens Explorer page
2. Frontend requests /api/v1/graph/subgraph
3. Backend checks Redis cache
4. If miss: Query Neo4j, format as Cytoscape JSON
5. Cache result, return to frontend
6. Cytoscape.js renders graph
7. User interactions trigger node selection events
8. Node details panel updates via Zustand store
```

### Algorithm Execution Flow

```
1. User clicks "Run Algorithm" on Dashboard
2. POST /api/v1/algorithms/run/{name}
3. Backend executes Cypher queries
4. Results written to node properties
5. Cache invalidated
6. Frontend refetches data
```

## Deployment

### Development
```bash
# Start services
docker-compose up -d neo4j redis

# Run backend
cd backend && uvicorn app.main:app --reload

# Run frontend
cd frontend && npm run dev
```

### Production

**Backend:**
- Docker container with gunicorn + uvicorn workers
- Environment variables for configuration
- Health check endpoint for orchestration

**Frontend:**
- Static build deployed to Vercel/Netlify
- API proxy to backend
- Environment-based API URL configuration

**Infrastructure:**
- Neo4j: Managed instance (Aura) or self-hosted cluster
- Redis: Managed instance (Redis Labs) or self-hosted
- Load balancer for API scaling

## Security Considerations

1. **API Authentication** - Implement API keys or OAuth2 for production
2. **CORS** - Configured for specific origins
3. **Input Validation** - Pydantic models validate all inputs
4. **Query Injection** - Parameterized Cypher queries prevent injection
5. **Rate Limiting** - Implement for production deployments

## Performance Optimization

1. **Database Indexes** - Created for frequent query patterns
2. **Query Pagination** - All list endpoints support skip/limit
3. **Caching** - Redis caches expensive computations
4. **Batch Processing** - Algorithm execution uses batched writes
5. **Approximate Algorithms** - Use sampling for large graphs

## Future Enhancements

1. **Real-time Updates** - WebSocket for live graph changes
2. **Graph Algorithms** - Integration with Neo4j GDS library
3. **Advanced NLQ** - Full LangChain integration with GPT-4
4. **Export/Import** - GraphML, GEXF format support
5. **Time-series Analysis** - Track bottleneck changes over time
6. **Alerting** - Notify when new bottlenecks emerge
