"""
商品业务服务层

封装商品搜索逻辑，包含:
1. 多数据库兼容搜索（MySQL全文索引 / openGauss GIN / SQLite LIKE）
2. Redis 缓存（首页热门商品）
3. 查询性能计时
"""
import json
import time
import logging
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.item import Item
from app.models.user import User
from app.core.database import DBType, db_manager
from app.core.redis import get_cache, set_cache, delete_cache
from app.services.search_compat import build_keyword_condition, build_explain_sql
from sqlalchemy import text

logger = logging.getLogger(__name__)

CACHE_KEY_HOME = "home:items:latest"
CACHE_EXPIRE = 300  # 5分钟


async def create_item(
    db: AsyncSession,
    user_id: int,
    title: str,
    price: float,
    description: Optional[str] = None,
    original_price: Optional[float] = None,
    category_id: Optional[int] = None,
    condition: int = 0,
    images: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Item:
    """创建商品"""
    new_item = Item(
        user_id=user_id,
        title=title,
        description=description,
        price=price,
        original_price=original_price,
        category_id=category_id,
        condition=condition,
        images=images,
        latitude=latitude,
        longitude=longitude,
        status=0,
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    # 清除首页缓存
    await delete_cache(CACHE_KEY_HOME)
    return new_item


async def search_items(
    db: AsyncSession,
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    status: int = 0,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[dict], int, float, DBType]:
    """
    商品搜索 - 演示索引优化效果
    返回: (items, total, query_time_ms, db_type)
    """
    db_type = db_manager.get_active_db_type()

    conditions = [Item.status == status]

    if keyword:
        conditions.append(build_keyword_condition(keyword))
    if category_id is not None:
        conditions.append(Item.category_id == category_id)
    if min_price is not None:
        conditions.append(Item.price >= min_price)
    if max_price is not None:
        conditions.append(Item.price <= max_price)

    # 查询总数
    count_query = select(func.count()).select_from(Item).where(and_(*conditions))
    total = (await db.execute(count_query)).scalar() or 0

    query = (
        select(Item, User.username, User.reputation_score)
        .outerjoin(User, Item.user_id == User.user_id)
        .where(and_(*conditions))
        .order_by(Item.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    start = time.time()
    result = await db.execute(query)
    rows = result.all()
    elapsed = (time.time() - start) * 1000

    serialized = [
        {
            "item_id": i.item_id,
            "title": i.title,
            "price": float(i.price) if i.price else 0,
            "original_price": float(i.original_price) if i.original_price else None,
            "status": i.status,
            "condition": i.condition,
            "images": i.images,
            "category_id": i.category_id,
            "view_count": i.view_count,
            "seller_id": i.user_id,
            "seller_name": seller_name if seller_name else "匿名用户",
            "seller_score": float(seller_score) if seller_score is not None else 5.0,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        }
        for i, seller_name, seller_score in rows
    ]

    return serialized, total, round(elapsed, 2), db_type


async def get_explain_plan(db: AsyncSession, keyword: str) -> dict:
    """获取 EXPLAIN 执行计划（用于演示索引优化效果）"""
    db_type = db_manager.get_active_db_type()
    sql = build_explain_sql(keyword, db_type)

    if db_type == DBType.SQLITE:
        result = await db.execute(text(sql), {"keyword": f"%{keyword}%"})
    else:
        result = await db.execute(text(sql), {"keyword": keyword})

    rows = result.fetchall()
    return {
        "db_type": db_type.value,
        "execution_plan": [dict(row._mapping) for row in rows],
    }


async def get_item_detail(db: AsyncSession, item_id: int) -> Optional[dict]:
    """获取商品详情并增加浏览量（原子更新，减少事务开销）"""
    result = await db.execute(
        select(Item, User.username, User.reputation_score)
        .outerjoin(User, Item.user_id == User.user_id)
        .where(Item.item_id == item_id)
    )
    row = result.first()
    if not row:
        return None
    item, seller_name, seller_score = row

    # 原子更新：UPDATE items SET view_count = view_count + 1 WHERE item_id = ?
    # 避免先读后写的竞态条件，减少行锁持有时间
    from sqlalchemy import update as sa_update
    await db.execute(
        sa_update(Item)
        .where(Item.item_id == item_id)
        .values(view_count=Item.view_count + 1)
    )
    await db.commit()
    await db.refresh(item)

    return {
        "item_id": item.item_id,
        "title": item.title,
        "description": item.description,
        "price": float(item.price) if item.price else 0,
        "original_price": float(item.original_price) if item.original_price else None,
        "category_id": item.category_id,
        "condition": item.condition,
        "status": item.status,
        "images": item.images.split(",") if item.images else [],
        "user_id": item.user_id,
        "seller_name": seller_name if seller_name else "匿名用户",
        "seller_score": float(seller_score) if seller_score is not None else 5.0,
        "view_count": item.view_count,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


async def get_home_items_cached(db: AsyncSession, limit: int = 20) -> dict:
    """获取首页商品列表（带 Redis 缓存）"""
    cached = await get_cache(CACHE_KEY_HOME)
    if cached:
        try:
            return json.loads(cached)
        except (json.JSONDecodeError, TypeError):
            pass

    # 查询在售商品总数
    count_query = select(func.count()).select_from(Item).where(Item.status == 0)
    total = (await db.execute(count_query)).scalar() or 0

    query = (
        select(Item, User.username, User.reputation_score)
        .outerjoin(User, Item.user_id == User.user_id)
        .where(Item.status == 0)
        .order_by(Item.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    rows = result.all()

    serialized = [
        {
            "item_id": i.item_id,
            "title": i.title,
            "price": float(i.price) if i.price else 0,
            "original_price": float(i.original_price) if i.original_price else None,
            "images": i.images,
            "status": i.status,
            "condition": i.condition,
            "category_id": i.category_id,
            "view_count": i.view_count,
            "seller_id": i.user_id,
            "seller_name": seller_name if seller_name else "匿名用户",
            "seller_score": float(seller_score) if seller_score is not None else 5.0,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        }
        for i, seller_name, seller_score in rows
    ]

    result_data = {"items": serialized, "total": total}
    await set_cache(CACHE_KEY_HOME, json.dumps(result_data, ensure_ascii=False), CACHE_EXPIRE)
    return result_data
