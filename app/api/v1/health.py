from fastapi import APIRouter
from app.core.database import db_manager
from app.core.config import settings
from app.core.redis import is_redis_available

router = APIRouter(prefix="/health", tags=["系统"])


@router.get("/")
async def health_check():
    """系统健康检查"""
    db_type = db_manager.get_active_db_type()
    return {
        "status": "healthy",
        "active_db": db_type.value if db_type else "unknown",
        "mysql_healthy": db_manager._mysql_healthy,
        "opengauss_healthy": db_manager._opengauss_healthy,
        "redis_available": is_redis_available(),
        "strategy": settings.db_strategy,
        "app": settings.app_name,
    }


@router.get("/db-status")
async def db_status():
    """数据库状态详情"""
    db_type = db_manager.get_active_db_type()
    return {
        "active_db": db_type.value if db_type else "unknown",
        "databases": {
            "mysql": {
                "healthy": db_manager._mysql_healthy,
                "url": settings.mysql_database_url.replace(settings.mysql_password, "***") if settings.mysql_password else settings.mysql_database_url,
            },
            "opengauss": {
                "healthy": db_manager._opengauss_healthy,
                "url": settings.opengauss_database_url.replace(settings.opengauss_password, "***") if settings.opengauss_password else settings.opengauss_database_url,
            },
            "sqlite": {
                "url": settings.sqlite_database_url,
            },
        },
    }
