from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.item import Item
from app.models.request import Request
from app.models.review import Review
from app.models.message import Message
from app.models.category import Category
from app.core.database import get_db
from app.core.security import get_admin_user
from app.core.redis import clear_cache_pattern
from app.services.item_service import CACHE_KEY_HOME
from app.utils.response import success, error
from passlib.context import CryptContext

router = APIRouter(prefix="/admin", tags=["管理"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 管理员缓存 key 前缀
ADMIN_USER_CACHE = "admin:user_list:*"
ADMIN_ITEM_CACHE = "admin:item_list:*"
ADMIN_TX_CACHE = "admin:transaction_list:*"


async def invalidate_admin_caches():
    """清除管理员相关缓存"""
    await clear_cache_pattern(ADMIN_USER_CACHE)
    await clear_cache_pattern(ADMIN_ITEM_CACHE)
    await clear_cache_pattern(ADMIN_TX_CACHE)
    await clear_cache_pattern("stats:dashboard")


# ==================== 用户管理 ====================

@router.get("/users")
async def admin_list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: str = Query("", description="搜索关键词"),
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """管理员：分页获取用户列表（支持搜索）"""
    conditions = []
    if keyword:
        conditions.append(
            or_(
                User.username.contains(keyword),
                User.email.contains(keyword),
                User.school.contains(keyword),
            )
        )

    base_query = select(User)
    if conditions:
        base_query = base_query.where(*conditions)

    total = (await db.scalar(select(func.count()).select_from(base_query.subquery()))) or 0

    result = await db.execute(
        base_query.order_by(User.user_id).offset((page - 1) * page_size).limit(page_size)
    )
    users = result.scalars().all()
    return success({
        "items": [
            {
                "user_id": u.user_id,
                "username": u.username,
                "email": u.email,
                "phone": u.phone,
                "school": u.school,
                "reputation_score": float(u.reputation_score) if u.reputation_score else 5.0,
                "is_admin": bool(u.is_admin),
                "is_active": bool(u.is_active),
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


class UserStatusUpdate(BaseModel):
    is_active: bool


@router.put("/users/{user_id}/status")
async def admin_update_user_status(
    user_id: int,
    body: UserStatusUpdate,
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """管理员：启用/禁用用户"""
    if user_id == 1 and not body.is_active:
        return error("不能禁用超级管理员", 400)
    user = (await db.execute(select(User).where(User.user_id == user_id))).scalar_one_or_none()
    if not user:
        return error("用户不存在", 404)
    user.is_active = body.is_active
    await db.commit()
    await invalidate_admin_caches()
    return success({"user_id": user_id, "is_active": body.is_active}, "状态已更新")


class PasswordReset(BaseModel):
    new_password: str


@router.put("/users/{user_id}/password")
async def admin_reset_user_password(
    user_id: int,
    body: PasswordReset,
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """管理员：重置用户密码"""
    user = (await db.execute(select(User).where(User.user_id == user_id))).scalar_one_or_none()
    if not user:
        return error("用户不存在", 404)
    user.password_hash = pwd_context.hash(body.new_password)
    await db.commit()
    return success({"user_id": user_id}, "密码已重置")


# ==================== 商品管理 ====================

@router.get("/items")
async def admin_list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: int = Query(-1, description="-1全部 0在售 1已预订 2已售出 3下架"),
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """管理员：分页获取商品列表（含卖家信息）"""
    conditions = []
    if status >= 0:
        conditions.append(Item.status == status)
    base_query = select(Item, User.username, User.reputation_score).outerjoin(
        User, Item.user_id == User.user_id
    )
    if conditions:
        base_query = base_query.where(*conditions)

    total = (await db.scalar(select(func.count()).select_from(base_query.subquery()))) or 0

    result = await db.execute(
        base_query.order_by(Item.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = result.all()
    return success({
        "items": [
            {
                "item_id": i.item_id,
                "title": i.title,
                "price": float(i.price) if i.price else 0,
                "original_price": float(i.original_price) if i.original_price else None,
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
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.put("/items/{item_id}/audit")
async def admin_audit_item(
    item_id: int,
    body: dict,
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """管理员：审核/下架商品（0在售 1已预订 2已售出 3下架）"""
    result = await db.execute(select(Item).where(Item.item_id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        return error("商品不存在", 404)
    new_status = body.get("status", 0)
    item.status = new_status
    await db.commit()
    # 清除首页和管理员缓存
    from app.core.redis import delete_cache
    await delete_cache(CACHE_KEY_HOME)
    await invalidate_admin_caches()
    return success({"item_id": item_id, "status": new_status}, "审核完成")


@router.delete("/items/{item_id}")
async def admin_delete_item(
    item_id: int,
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """管理员：删除商品"""
    result = await db.execute(select(Item).where(Item.item_id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        return error("商品不存在", 404)
    await db.delete(item)
    await db.commit()
    from app.core.redis import delete_cache
    await delete_cache(CACHE_KEY_HOME)
    await invalidate_admin_caches()
    return success({"item_id": item_id}, "已删除")


# ==================== 交易管理 ====================

@router.get("/transactions")
async def admin_list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: int = Query(-1, description="-1全部 0待处理 1已接受 2已拒绝 3已完成"),
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """管理员：分页获取交易列表"""
    conditions = []
    if status >= 0:
        conditions.append(Request.status == status)

    base_query = select(Request, Item.title, User.username).outerjoin(
        Item, Request.item_id == Item.item_id
    ).outerjoin(User, Request.requester_id == User.user_id)
    if conditions:
        base_query = base_query.where(*conditions)

    total = (await db.scalar(select(func.count()).select_from(base_query.subquery()))) or 0

    result = await db.execute(
        base_query.order_by(Request.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = result.all()
    return success({
        "items": [
            {
                "request_id": r.request_id,
                "item_id": r.item_id,
                "item_title": item_title if item_title else "",
                "requester_id": r.requester_id,
                "requester_name": requester_name if requester_name else "匿名",
                "seller_id": r.seller_id,
                "status": r.status,
                "trade_code": r.trade_code,
                "message": r.message,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r, item_title, requester_name in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


# ==================== 评价管理 ====================

@router.get("/reviews")
async def admin_list_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """管理员：分页获取评价列表"""
    total = (await db.scalar(select(func.count(Review.review_id)))) or 0
    result = await db.execute(
        select(Review, User.username).outerjoin(User, Review.reviewer_id == User.user_id)
        .order_by(Review.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = result.all()
    return success({
        "items": [
            {
                "review_id": r.review_id,
                "request_id": r.request_id,
                "reviewer_id": r.reviewer_id,
                "reviewer_name": reviewer_name if reviewer_name else "匿名",
                "reviewee_id": r.reviewee_id,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r, reviewer_name in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.delete("/reviews/{review_id}")
async def admin_delete_review(
    review_id: int,
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """管理员：删除违规评价"""
    review = (await db.execute(select(Review).where(Review.review_id == review_id))).scalar_one_or_none()
    if not review:
        return error("评价不存在", 404)
    await db.delete(review)
    await db.commit()
    return success({"review_id": review_id}, "已删除")


# ==================== 消息管理 ====================

@router.get("/messages")
async def admin_list_messages(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """管理员：分页获取消息列表"""
    total = (await db.scalar(select(func.count(Message.msg_id)))) or 0
    result = await db.execute(
        select(Message, User.username).outerjoin(User, Message.sender_id == User.user_id)
        .order_by(Message.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = result.all()
    return success({
        "items": [
            {
                "msg_id": m.msg_id,
                "sender_id": m.sender_id,
                "sender_name": sender_name if sender_name else "系统",
                "receiver_id": m.receiver_id,
                "item_id": m.item_id,
                "title": m.title,
                "content": m.content,
                "is_read": m.is_read,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m, sender_name in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


# ==================== 统计 ====================

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
