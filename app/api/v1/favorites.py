from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.favorite import Favorite
from app.models.item import Item
from app.core.database import get_db
from app.core.security import get_current_user
from app.utils.response import success, error
from app.schemas.favorite import FavoriteCreate

router = APIRouter(prefix="/favorites", tags=["收藏"])


@router.post("/")
async def add_favorite(
    req: FavoriteCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """收藏商品"""
    existing = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user["user_id"],
            Favorite.item_id == req.item_id,
        )
    )
    if existing.scalar_one_or_none():
        return error("已收藏过该商品", 400)

    fav = Favorite(user_id=current_user["user_id"], item_id=req.item_id)
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return success({"favorite_id": fav.favorite_id}, "收藏成功")


@router.get("/")
async def list_favorites(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取我的收藏列表（含商品信息）"""
    result = await db.execute(
        select(Favorite, Item)
        .join(Item, Favorite.item_id == Item.item_id)
        .where(Favorite.user_id == current_user["user_id"])
        .order_by(Favorite.created_at.desc())
    )
    rows = result.all()
    return success([
        {
            "favorite_id": fav.favorite_id,
            "item_id": item.item_id,
            "title": item.title,
            "price": float(item.price) if item.price else 0,
            "status": item.status,
            "images": item.images,
            "created_at": fav.created_at.isoformat() if fav.created_at else None,
        }
        for fav, item in rows
    ])


@router.delete("/{item_id}")
async def remove_favorite(
    item_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """取消收藏"""
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user["user_id"],
            Favorite.item_id == item_id,
        )
    )
    fav = result.scalar_one_or_none()
    if not fav:
        return error("未收藏该商品", 404)
    await db.delete(fav)
    await db.commit()
    return success({"item_id": item_id}, "取消收藏成功")
