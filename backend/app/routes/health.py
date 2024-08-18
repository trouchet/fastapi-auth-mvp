
from fastapi import APIRouter

from backend.app.base.config import settings

from backend.app.utils.healthcheck import (
    is_server_live,
    is_memory_usage_within_limits,
    is_database_healthy,
    is_cache_healthy,
    healthcheck_dict,
)

router=APIRouter(prefix='/health', tags=["Health"])


@router.get("/")
async def health():
    is_db_healthy, db_error = await is_database_healthy()
    is_c_healthy, cache_error = await is_cache_healthy()
    is_m_healthy, memory_error = await is_memory_usage_within_limits()

    # Perform various health checks and consolidate results
    return {
        "database": healthcheck_dict(is_db_healthy, db_error),
        "cache": healthcheck_dict(is_c_healthy, cache_error),
        "memory": healthcheck_dict(is_m_healthy, memory_error) 
    }


@router.get("/liveness")
async def liveness():
    is_memory_usage_low, memory_error = await is_memory_usage_within_limits()
    is_live, live_error = await is_server_live()
    
    # Perform basic liveness checks (e.g., database connection)
    return {
        "memory": healthcheck_dict(is_memory_usage_low, memory_error),
        "live": healthcheck_dict(is_live, live_error)
    }


@router.get("/readiness")
async def readiness():
    # Perform more intensive readiness checks (e.g., data availability)    
    return {"status": "ready"}