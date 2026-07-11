import redis.asyncio as redis
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password or None,
    db=settings.redis_db,
    decode_responses=True,
)

_redis_available = False


async def check_redis_health() -> bool:
    """检查 Redis 连接是否可用"""
    global _redis_available
    try:
        await redis_client.ping()
        _redis_available = True
        logger.info("✅ Redis 健康检查通过")
    except Exception as e:
        _redis_available = False
        logger.warning(f"⚠️ Redis 不可用（缓存功能将降级）: {e}")
    return _redis_available


def is_redis_available() -> bool:
    return _redis_available


async def get_cache(key: str) -> str:
    if not _redis_available:
        return None
    try:
        return await redis_client.get(key)
    except Exception:
        return None


async def set_cache(key: str, value: str, expire: int = 300):
    if not _redis_available:
        return
    try:
        await redis_client.setex(key, expire, value)
    except Exception:
        pass


async def delete_cache(key: str):
    if not _redis_available:
        return
    try:
        await redis_client.delete(key)
    except Exception:
        pass


async def clear_cache_pattern(pattern: str):
    if not _redis_available:
        return
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
    except Exception:
        pass
