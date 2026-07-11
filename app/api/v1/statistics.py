import json
from fastapi import APIRouter, Depends
from sqlalchemy import text, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.item import Item
from app.models.request import Request
from app.models.category import Category
from app.core.database import get_db, DBType, db_manager
from app.core.redis import get_cache, set_cache
from app.core.security import get_current_user
from app.utils.response import success

router = APIRouter(prefix="/statistics", tags=["统计"])

CACHE_KEY_DASHBOARD = "stats:dashboard"
CACHE_EXPIRE_DASHBOARD = 300  # 5分钟


@router.get("/dashboard")
async def get_dashboard(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """数据看板统计（带 Redis 缓存，5分钟过期）"""
    # 1. 尝试读取缓存
    cached = await get_cache(CACHE_KEY_DASHBOARD)
    if cached:
        try:
            data = json.loads(cached)
            data["cached"] = True
            return success(data)
        except (json.JSONDecodeError, TypeError):
            pass

    db_type = db_manager.get_active_db_type()

    # 整体统计
    total_users = await db.scalar(select(func.count(User.user_id)))
    total_items = await db.scalar(select(func.count(Item.item_id)))
    available_items = await db.scalar(
        select(func.count(Item.item_id)).where(Item.status == 0)
    )
    completed_orders = await db.scalar(
        select(func.count(Request.request_id)).where(Request.status == 3)
    )

    # 商品分类占比（关联 categories 表获取分类名称）
    cat_query = (
        select(Category.name, func.count(Item.item_id))
        .outerjoin(Category, Item.category_id == Category.category_id)
        .where(Item.status == 0)
        .group_by(Category.name)
    )
    cat_result = await db.execute(cat_query)
    categories = [
        {"name": row[0] if row[0] else "未分类", "count": row[1]}
        for row in cat_result
    ]

    # 价格区间分布
    price_data = await db.execute(
        select(Item.price).where(Item.status == 0, Item.price > 0).order_by(Item.price)
    )
    prices = [float(row[0]) for row in price_data if row[0]]
    price_ranges = _build_price_ranges(prices)

    # 交易趋势（近7天，使用 SQLAlchemy 日期函数兼容）
    trend_result = await db.execute(
        select(
            func.date(Request.created_at).label("date"),
            func.count(Request.request_id).label("count"),
        )
        .where(Request.status == 3)
        .group_by(func.date(Request.created_at))
        .order_by(text("date"))
        .limit(7)
    )
    trend = [
        {
            "date": str(row[0]) if row[0] else "",
            "count": row[1],
        }
        for row in trend_result
    ]

    result_data = {
        "trend": trend,
        "categories": categories,
        "price_ranges": price_ranges,
        "overview": {
            "total_users": total_users or 0,
            "total_items": total_items or 0,
            "available_items": available_items or 0,
            "completed_orders": completed_orders or 0,
        },
        "db_type": db_type.value,
        "cached": False,
    }

    # 2. 写入缓存
    await set_cache(
        CACHE_KEY_DASHBOARD,
        json.dumps(result_data, ensure_ascii=False),
        CACHE_EXPIRE_DASHBOARD,
    )

    return success(result_data)


def _build_price_ranges(prices: list, step: int = 50) -> list:
    """构建价格区间分布"""
    if not prices:
        return []
    ranges = {}
    for p in prices:
        bucket = int(p // step) * step
        key = f"{bucket}-{bucket + step}"
        ranges[key] = ranges.get(key, 0) + 1
    return [{"range": k, "count": v} for k, v in sorted(ranges.items())]
