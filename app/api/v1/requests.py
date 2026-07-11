from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.request import Request
from app.models.item import Item
from app.models.user import User
from app.models.review import Review
from app.core.database import get_db
from app.core.security import get_current_user
from app.utils.response import success, error
from app.schemas.request import RequestCreate
from app.services import request_service

router = APIRouter(prefix="/requests", tags=["交易"])


class ConfirmCode(BaseModel):
    code: str


@router.post("/")
async def create_request(
    req: RequestCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发起交易请求 - 异步事务 + 行锁"""
    result = await request_service.create_request(
        db=db,
        item_id=req.item_id,
        requester_id=current_user["user_id"],
        requester_name=current_user["username"],
        message=req.message,
    )

    if result.get("error"):
        return error(result["error"], result.get("code", 500))
    return success({"request_id": result.get("request_id")}, result.get("message", "成功"))


@router.put("/{request_id}/status")
async def update_request_status(
    request_id: int,
    status: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """卖家更新交易状态 (1:接受 2:拒绝)，完成需用 /confirm 接口"""
    result = await request_service.update_request_status(
        db=db,
        request_id=request_id,
        new_status=status,
        current_user_id=current_user["user_id"],
    )

    if result.get("error"):
        return error(result["error"], result.get("code", 500))
    return success({
        "request_id": result.get("request_id"),
        "status": result.get("status"),
        "trade_code": result.get("trade_code"),
    }, result.get("message", "成功"))


@router.post("/{request_id}/confirm")
async def confirm_with_code(
    request_id: int,
    body: ConfirmCode,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """买家输入交易码确认收货，完成交易"""
    result = await request_service.confirm_with_code(
        db=db,
        request_id=request_id,
        code=body.code,
        buyer_id=current_user["user_id"],
    )

    if result.get("error"):
        return error(result["error"], result.get("code", 500))
    return success({
        "request_id": result.get("request_id"),
        "status": result.get("status"),
    }, result.get("message", "成功"))


@router.get("/my")
async def get_my_requests(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    as_buyer: bool = Query(True),
):
    """获取我的交易列表（含商品信息与对方信息）"""
    if as_buyer:
        # 我买的：对方是卖家
        result = await db.execute(
            select(Request, Item, User.username)
            .join(Item, Request.item_id == Item.item_id)
            .join(User, Request.seller_id == User.user_id)
            .where(Request.requester_id == current_user["user_id"])
            .order_by(Request.created_at.desc())
        )
    else:
        # 我卖的：对方是买家
        result = await db.execute(
            select(Request, Item, User.username)
            .join(Item, Request.item_id == Item.item_id)
            .join(User, Request.requester_id == User.user_id)
            .where(Request.seller_id == current_user["user_id"])
            .order_by(Request.created_at.desc())
        )

    rows = result.all()

    # 批量查询当前用户对这些交易是否已评价（避免 N+1 查询）
    request_ids = [r.request_id for r, _, _ in rows]
    reviewed_set = set()
    if request_ids:
        reviewed_result = await db.execute(
            select(Review.request_id).where(
                Review.request_id.in_(request_ids),
                Review.reviewer_id == current_user["user_id"],
            )
        )
        reviewed_set = {row[0] for row in reviewed_result.all()}

    return success([
        {
            "request_id": r.request_id,
            "item_id": r.item_id,
            "item_title": item.title,
            "item_price": float(item.price) if item.price else 0,
            "item_images": item.images,
            "item_status": item.status,
            "status": r.status,
            "trade_code": r.trade_code,
            "message": r.message,
            # 对方信息（用于交易后联系对方）
            "peer_id": r.seller_id if as_buyer else r.requester_id,
            "peer_name": peer_name,
            # 是否已评价（仅已完成交易时有意义）
            "has_reviewed": r.request_id in reviewed_set,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r, item, peer_name in rows
    ])
