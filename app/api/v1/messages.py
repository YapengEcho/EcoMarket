from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, or_, and_, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message
from app.models.user import User
from app.core.database import get_db
from app.core.redis import get_cache, set_cache, delete_cache
from app.core.security import get_current_user
from app.utils.response import success, error

router = APIRouter(prefix="/messages", tags=["消息"])

CACHE_EXPIRE_UNREAD = 300  # 未读数缓存 5 分钟


def _unread_cache_key(user_id: int) -> str:
    """按用户生成未读消息数缓存键"""
    return f"messages:unread:{user_id}"


class SendMessage(BaseModel):
    receiver_id: int
    content: str
    item_id: int | None = None
    title: str | None = None


@router.get("/")
async def get_messages(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    unread_only: bool = Query(False),
):
    """获取我的消息列表（含发送者用户名）"""
    query = (
        select(Message, User.username)
        .outerjoin(User, Message.sender_id == User.user_id)
        .where(Message.receiver_id == current_user["user_id"])
    )
    if unread_only:
        query = query.where(Message.is_read == False)
    query = query.order_by(Message.created_at.desc())

    result = await db.execute(query)
    rows = result.all()
    return success([
        {
            "msg_id": m.msg_id,
            "sender_id": m.sender_id,
            "sender_name": username if username else "系统通知",
            "title": m.title,
            "content": m.content,
            "is_read": m.is_read,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m, username in rows
    ])


@router.post("/")
async def send_message(
    body: SendMessage,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送站内消息（用户间双向通信，用于交易后协商时间地点）"""
    sender_id = current_user["user_id"]

    # 不能给自己发消息
    if body.receiver_id == sender_id:
        return error("不能给自己发消息", 400)

    # 校验对方存在
    peer = await db.execute(select(User).where(User.user_id == body.receiver_id))
    if not peer.scalar_one_or_none():
        return error("接收方不存在", 404)

    # content 长度校验（模型字段限制 1000）
    if len(body.content) > 1000:
        return error("消息内容不能超过 1000 字", 400)

    msg = Message(
        sender_id=sender_id,
        receiver_id=body.receiver_id,
        item_id=body.item_id,
        title=body.title,
        content=body.content,
        is_read=False,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    # 清除接收方未读数缓存
    await delete_cache(_unread_cache_key(body.receiver_id))

    return success({"msg_id": msg.msg_id}, "发送成功")


@router.get("/conversation/{item_id}")
async def get_conversation(
    item_id: int,
    peer_id: int = Query(..., description="对方用户ID"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    查询某商品下我与对方的对话历史（基于商品，非基于用户对）。
    返回后自动把对方发给我的未读消息标记为已读。
    """
    me = current_user["user_id"]
    peer = peer_id

    # 查询该商品下双向消息：我发给他 OR 他发给我
    result = await db.execute(
        select(Message, User.username)
        .outerjoin(User, Message.sender_id == User.user_id)
        .where(
            Message.item_id == item_id,
            or_(
                and_(Message.sender_id == me, Message.receiver_id == peer),
                and_(Message.sender_id == peer, Message.receiver_id == me),
            ),
        )
        .order_by(Message.created_at.asc())
    )
    rows = result.all()

    # 对方发给我且未读的消息标记为已读
    unread_ids = [m.msg_id for m, _ in rows if m.receiver_id == me and not m.is_read]
    if unread_ids:
        await db.execute(
            update(Message)
            .where(Message.msg_id.in_(unread_ids))
            .values(is_read=True)
        )
        await db.commit()
        # 清除我的未读数缓存
        await delete_cache(_unread_cache_key(me))

    return success([
        {
            "msg_id": m.msg_id,
            "sender_id": m.sender_id,
            "sender_name": username if m.sender_id != 0 and username else "系统通知",
            "is_mine": m.sender_id == me,
            "title": m.title,
            "content": m.content,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m, username in rows
    ])


@router.put("/{msg_id}/read")
async def mark_as_read(
    msg_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """标记消息为已读（同时清除该用户的未读数缓存）"""
    result = await db.execute(
        select(Message).where(Message.msg_id == msg_id)
    )
    msg = result.scalar_one_or_none()
    if not msg:
        return error("消息不存在", 404)
    if msg.receiver_id != current_user["user_id"]:
        return error("无权操作", 403)

    msg.is_read = True
    await db.commit()

    # 缓存失效：读取后清除，下次查询将重新从数据库获取最新值
    await delete_cache(_unread_cache_key(current_user["user_id"]))

    return success({"msg_id": msg_id}, "已标记为已读")


@router.get("/unread/count")
async def get_unread_count(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取未读消息数（使用 COUNT 聚合 + Redis 缓存，读取后失效）"""
    cache_key = _unread_cache_key(current_user["user_id"])

    # 1. 尝试读取缓存
    cached = await get_cache(cache_key)
    if cached is not None:
        try:
            return success({"unread_count": int(cached), "cached": True})
        except (ValueError, TypeError):
            pass

    # 2. 缓存未命中，查询数据库
    result = await db.execute(
        select(func.count(Message.msg_id))
        .where(Message.receiver_id == current_user["user_id"], Message.is_read == False)
    )
    count = result.scalar() or 0

    # 3. 写入缓存（5分钟过期，或在标记已读时主动失效）
    await set_cache(cache_key, str(count), CACHE_EXPIRE_UNREAD)

    return success({"unread_count": count, "cached": False})
