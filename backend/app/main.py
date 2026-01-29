"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.services.neo4j_service import neo4j_service
from app.api.v1 import router as api_v1_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    logger.info("Starting Social Network Bottleneck Detector API...")
    try:
        neo4j_service.verify_connectivity()
        logger.info("Neo4j connection verified")
    except Exception as e:
        logger.warning(f"Neo4j connection failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    neo4j_service.close()
    logger.info("Neo4j connection closed")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    # Social Network Bottleneck Detector API
    
    Detect and analyze bottleneck nodes in social networks using graph algorithms.
    
    ## Features
    - **Graph Analysis**: Betweenness centrality, PageRank, community detection
    - **Bottleneck Detection**: Identify critical nodes connecting communities
    - **Natural Language Queries**: Ask questions in plain English
    - **Visualization**: Export graph data for Cytoscape.js
    """,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_v1_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    neo4j_status = "healthy"
    try:
        neo4j_service.verify_connectivity()
    except Exception:
        neo4j_status = "unhealthy"
    
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "services": {
            "neo4j": neo4j_status
        }
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }
