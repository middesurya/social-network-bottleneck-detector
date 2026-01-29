"""API v1 router aggregation."""
from fastapi import APIRouter

from app.api.v1.users import router as users_router
from app.api.v1.graph import router as graph_router
from app.api.v1.algorithms import router as algorithms_router
from app.api.v1.bottlenecks import router as bottlenecks_router
from app.api.v1.communities import router as communities_router
from app.api.v1.nlq import router as nlq_router

router = APIRouter()

router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(graph_router, prefix="/graph", tags=["Graph"])
router.include_router(algorithms_router, prefix="/algorithms", tags=["Algorithms"])
router.include_router(bottlenecks_router, prefix="/bottlenecks", tags=["Bottlenecks"])
router.include_router(communities_router, prefix="/communities", tags=["Communities"])
router.include_router(nlq_router, prefix="/nlq", tags=["Natural Language"])
