from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.item import Item
from app.models.request import Request
from app.core.database import get_db
from app.core.security import get_admin_user
from app.utils.response import success, error

router = APIRouter(prefix="/admin", tags=["管理"])


@router.get("/users")
async def admin_list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """管理员：分页获取用户列表"""
    # 查询总数
    total = (await db.execute(select(func.count(User.user_id)))).scalar() or 0

    # 分页查询
    result = await db.execute(
        select(User)
        .order_by(User.user_id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    users = result.scalars().all()
    return success({
        "items": [
            {
                "user_id": u.user_id,
                "username": u.username,
                "email": u.email,
                "school": u.school,
                "reputation_score": float(u.reputation_score) if u.reputation_score else 5.0,
                "is_admin": u.is_admin,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.put("/items/{item_id}/audit")
async def admin_audit_item(
    item_id: int,
    status: int = Query(..., description="0在售 1已预订 2已售出 3下架"),
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """管理员：审核/下架商品"""
    result = await db.execute(select(Item).where(Item.item_id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        return error("商品不存在", 404)
    item.status = status
    await db.commit()
    return success({"item_id": item_id, "status": status}, "审核完成")


@router.get("/stats")
async def admin_stats(
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """管理员：平台整体统计"""
    total_users = await db.scalar(select(func.count(User.user_id)))
    total_items = await db.scalar(select(func.count(Item.item_id)))
    pending_orders = await db.scalar(
        select(func.count(Request.request_id)).where(Request.status == 0)
    )
    return success({
        "total_users": total_users or 0,
        "total_items": total_items or 0,
        "pending_orders": pending_orders or 0,
    })
