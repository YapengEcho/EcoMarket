from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.item import Item
from app.core.database import get_db, db_manager
from app.core.security import get_current_user
from app.utils.response import success, error
from app.schemas.item import ItemCreate, ItemUpdate
from app.services import item_service
from app.core.redis import get_cache, set_cache, delete_cache
import json

router = APIRouter(prefix="/items", tags=["商品"])


@router.post("/")
async def create_item(
    item: ItemCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发布商品"""
    new_item = await item_service.create_item(
        db=db,
        user_id=current_user["user_id"],
        title=item.title,
        price=item.price,
        description=item.description,
        original_price=item.original_price,
        category_id=item.category_id,
        condition=item.condition,
        images=item.images,
    )
    return success({"item_id": new_item.item_id}, "商品发布成功")


@router.get("/")
async def list_items(
    status: int = Query(0),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取商品列表（首页，带 Redis 缓存）"""
    data = await item_service.get_home_items_cached(db, limit=page_size)
    return success({
        "items": data["items"],
        "page": page,
        "page_size": page_size,
        "total": data["total"],
    })


@router.get("/search")
async def search_items(
    keyword: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    status: int = Query(0),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    商品搜索 - 演示索引优化效果
    优化前: 全表扫描 ~1200ms
    优化后: 索引扫描 ~50ms
    """
    # 价格区间校验：最低价不能大于最高价
    if min_price is not None and max_price is not None and min_price > max_price:
        return error("最低价不能大于最高价", 400)

    items, total, query_time_ms, db_type = await item_service.search_items(
        db=db,
        keyword=keyword,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        status=status,
        page=page,
        page_size=page_size,
    )

    return success({
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "query_time_ms": query_time_ms,
        "db_type": db_type.value,
    })


@router.get("/explain")
async def explain_query(
    keyword: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """演示索引优化效果 - 返回 EXPLAIN 执行计划"""
    plan = await item_service.get_explain_plan(db, keyword)
    return success(plan)


@router.get("/{item_id}")
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """获取商品详情"""
    item_detail = await item_service.get_item_detail(db, item_id)
    if not item_detail:
        return error("商品不存在", 404)
    return success(item_detail)


@router.put("/{item_id}")
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新商品信息"""
    result = await db.execute(select(Item).where(Item.item_id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        return error("商品不存在", 404)
    if item.user_id != current_user["user_id"]:
        return error("无权修改他人商品", 403)

    if item_update.title is not None:
        item.title = item_update.title
    if item_update.description is not None:
        item.description = item_update.description
    if item_update.price is not None:
        item.price = item_update.price
    if item_update.status is not None:
        item.status = item_update.status
    if item_update.images is not None:
        item.images = item_update.images

    await db.commit()
    # 清除首页缓存：下架/修改商品后市集需刷新
    await delete_cache(item_service.CACHE_KEY_HOME)
    return success({"item_id": item_id}, "更新成功")


@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除商品"""
    result = await db.execute(select(Item).where(Item.item_id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        return error("商品不存在", 404)
    if item.user_id != current_user["user_id"]:
        return error("无权删除他人商品", 403)

    await db.delete(item)
    await db.commit()
    # 清除首页缓存：删除商品后市集需刷新
    await delete_cache(item_service.CACHE_KEY_HOME)
    return success({"item_id": item_id}, "删除成功")


@router.get("/my/items")
async def get_my_items(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取我发布的商品"""
    result = await db.execute(
        select(Item)
        .where(Item.user_id == current_user["user_id"])
        .order_by(Item.created_at.desc())
    )
    items = result.scalars().all()
    return success([
        {
            "item_id": i.item_id,
            "title": i.title,
            "price": float(i.price) if i.price else 0,
            "status": i.status,
            "view_count": i.view_count,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        }
        for i in items
    ])
