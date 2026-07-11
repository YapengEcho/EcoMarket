"""
交易请求业务服务层

核心: 异步事务 + 行锁 (SELECT ... FOR UPDATE)
防止超卖，保证数据一致性

交易流程（无资金流，线下交易）：
1. 买家下单 (create_request)：创建 Request，商品状态不变，允许多人同时发起请求
2. 卖家接受 (update_request_status=1)：商品变已预订，生成 6 位交易码，通知买家；其他待处理请求自动拒绝
3. 卖家拒绝 (update_request_status=2)：仅改 Request 状态，商品状态不变
4. 线下见面，买家输码确认 (confirm_with_code)：校验交易码，交易完成，商品变已售出
"""
import logging
import secrets
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.item import Item
from app.models.request import Request
from app.models.message import Message
from app.models.review import Review
from app.models.user import User
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def generate_trade_code() -> str:
    """生成 6 位数字交易码（密码学安全随机）"""
    return "".join(str(secrets.choice(range(10))) for _ in range(6))


async def create_request(
    db: AsyncSession, item_id: int, requester_id: int, requester_name: str, message: Optional[str] = None
) -> dict:
    """发起交易请求 - 异步事务 + 行锁

    商品状态不变（保持 status=0 在售），允许多人同时发起请求。
    只有卖家接受某请求时，商品才变已预订（status=1）。
    """
    try:
        async with db.begin():
            # ★ 行锁：SELECT ... FOR UPDATE 防止超卖
            result = await db.execute(
                select(Item).where(Item.item_id == item_id).with_for_update()
            )
            item = result.scalar_one_or_none()

            if not item:
                return {"error": "商品不存在", "code": 404}
            if item.status == 2:
                return {"error": "商品已售出", "code": 400}
            if item.user_id == requester_id:
                return {"error": "不能购买自己发布的商品", "code": 400}

            # 同一买家对同一商品只能有一个待处理/已接受的请求
            existing = await db.execute(
                select(Request).where(
                    Request.item_id == item_id,
                    Request.requester_id == requester_id,
                    Request.status.in_([0, 1]),
                )
            )
            if existing.scalar_one_or_none():
                return {"error": "您已对此商品发起过请求，请等待卖家处理", "code": 400}

            # 创建交易请求（商品状态不变，允许多人同时发起请求）
            request = Request(
                item_id=item_id,
                requester_id=requester_id,
                seller_id=item.user_id,
                status=0,
                message=message,
            )
            db.add(request)
            await db.flush()

            # 创建消息通知卖家
            msg = Message(
                sender_id=0,
                receiver_id=item.user_id,
                title="新的交易请求",
                content=f"用户 {requester_name} 想购买您的商品：{item.title}，请前往「我卖出的」处理",
            )
            db.add(msg)
            await db.flush()

            return {"request_id": request.request_id, "message": "交易请求已发送，等待卖家处理"}

    except SQLAlchemyError as e:
        logger.error(f"创建交易请求失败: {e}")
        return {"error": f"交易创建失败: {str(e)}", "code": 500}


async def update_request_status(
    db: AsyncSession, request_id: int, new_status: int, current_user_id: int
) -> dict:
    """更新交易状态 (0:待处理 1:已接受 2:已拒绝 3:已完成)

    接受(1)：生成 6 位交易码，通知买家
    拒绝(2)：商品恢复在售
    完成(3)：需通过 confirm_with_code 接口，不可直接调用
    """
    try:
        async with db.begin():
            result = await db.execute(
                select(Request)
                .where(Request.request_id == request_id)
                .with_for_update()
            )
            request = result.scalar_one_or_none()
            if not request:
                return {"error": "交易请求不存在", "code": 404}

            # 权限校验：只有卖家可以接受/拒绝
            if new_status in (1, 2) and request.seller_id != current_user_id:
                return {"error": "只有卖家可以处理此请求", "code": 403}

            old_status = request.status

            # 接受交易：生成交易码，商品变已预订，自动拒绝其他待处理请求
            if new_status == 1 and old_status == 0:
                # 锁定商品，更新为已预订
                item_result = await db.execute(
                    select(Item).where(Item.item_id == request.item_id).with_for_update()
                )
                item = item_result.scalar_one_or_none()
                if item and item.status == 2:
                    return {"error": "商品已售出，无法接受", "code": 400}
                if item:
                    item.status = 1
                    await db.flush()

                request.trade_code = generate_trade_code()
                request.status = 1
                await db.flush()
                # 通知买家
                msg = Message(
                    sender_id=0,
                    receiver_id=request.requester_id,
                    title="卖家已接受交易",
                    content=f"您的交易已被接受，交易码：{request.trade_code}。请在线下交易时将交易码告诉对方",
                )
                db.add(msg)
                await db.flush()

                # 自动拒绝该商品的其他待处理请求
                other_requests = await db.execute(
                    select(Request).where(
                        Request.item_id == request.item_id,
                        Request.request_id != request_id,
                        Request.status == 0,
                    )
                )
                for other in other_requests.scalars().all():
                    other.status = 2
                    await db.flush()
                    # 通知被拒绝的买家
                    decline_msg = Message(
                        sender_id=0,
                        receiver_id=other.requester_id,
                        title="交易请求已被拒绝",
                        content=f"卖家已接受其他买家的请求，您的请求已被自动拒绝",
                    )
                    db.add(decline_msg)
                    await db.flush()

                return {
                    "request_id": request_id,
                    "status": 1,
                    "trade_code": request.trade_code,
                    "message": "已接受交易，请在线下交易时将交易码告诉对方",
                }

            # 拒绝交易：仅改 Request 状态，商品状态不变
            if new_status == 2 and old_status == 0:
                request.status = 2
                await db.flush()
                # 通知买家
                msg = Message(
                    sender_id=0,
                    receiver_id=request.requester_id,
                    title="卖家拒绝了交易",
                    content=f"卖家已拒绝您的交易请求",
                )
                db.add(msg)
                await db.flush()
                return {"request_id": request_id, "status": 2, "message": "已拒绝交易"}

            return {"error": "不支持的状态转换", "code": 400}

    except SQLAlchemyError as e:
        logger.error(f"更新交易状态失败: {e}")
        return {"error": f"状态更新失败: {str(e)}", "code": 500}


async def confirm_with_code(
    db: AsyncSession, request_id: int, code: str, buyer_id: int
) -> dict:
    """买家输入交易码确认收货，完成交易"""
    try:
        async with db.begin():
            result = await db.execute(
                select(Request)
                .where(Request.request_id == request_id)
                .with_for_update()
            )
            request = result.scalar_one_or_none()
            if not request:
                return {"error": "交易请求不存在", "code": 404}

            if request.requester_id != buyer_id:
                return {"error": "只有买家可以确认收货", "code": 403}
            if request.status != 1:
                return {"error": "卖家尚未接受交易", "code": 400}
            if not request.trade_code:
                return {"error": "交易码异常，请联系卖家", "code": 400}
            if code.strip() != request.trade_code:
                return {"error": "交易码不正确", "code": 400}

            # 校验通过：交易完成，商品变已售出
            request.status = 3
            await db.flush()

            item_result = await db.execute(
                select(Item).where(Item.item_id == request.item_id).with_for_update()
            )
            item = item_result.scalar_one_or_none()
            if item:
                item.status = 2
                await db.flush()

            # 通知卖家
            msg = Message(
                sender_id=0,
                receiver_id=request.seller_id,
                title="交易已完成",
                content=f"买家已确认收货，交易 #{request_id} 完成",
            )
            db.add(msg)
            await db.flush()

            return {"request_id": request_id, "status": 3, "message": "交易完成"}

    except SQLAlchemyError as e:
        logger.error(f"确认收货失败: {e}")
        return {"error": f"确认失败: {str(e)}", "code": 500}


async def create_review(
    db: AsyncSession,
    request_id: int,
    reviewer_id: int,
    rating: int,
    comment: Optional[str] = None,
) -> dict:
    """创建评价并更新被评价者信誉分"""
    try:
        async with db.begin():
            result = await db.execute(
                select(Request).where(Request.request_id == request_id).with_for_update()
            )
            request = result.scalar_one_or_none()
            if not request:
                return {"error": "交易请求不存在", "code": 404}
            if request.status != 3:
                return {"error": "交易未完成，无法评价", "code": 400}

            if reviewer_id == request.requester_id:
                reviewee_id = request.seller_id
            elif reviewer_id == request.seller_id:
                reviewee_id = request.requester_id
            else:
                return {"error": "您不是此交易的参与方", "code": 403}

            existing = await db.execute(
                select(Review).where(
                    Review.request_id == request_id,
                    Review.reviewer_id == reviewer_id,
                )
            )
            if existing.scalar_one_or_none():
                return {"error": "您已对此交易评价过", "code": 400}

            review = Review(
                request_id=request_id,
                reviewer_id=reviewer_id,
                reviewee_id=reviewee_id,
                rating=rating,
                comment=comment,
            )
            db.add(review)
            await db.flush()

            # 更新被评价者信誉分（加权平均）
            user_result = await db.execute(
                select(User).where(User.user_id == reviewee_id).with_for_update()
            )
            user = user_result.scalar_one_or_none()
            if user:
                old_score = float(user.reputation_score or 5.0)
                new_score = old_score * 0.9 + rating * 0.1
                new_score = max(0, min(5, new_score))
                user.reputation_score = new_score
                await db.flush()

            return {"review_id": review.review_id, "message": "评价成功"}

    except SQLAlchemyError as e:
        logger.error(f"创建评价失败: {e}")
        return {"error": f"评价失败: {str(e)}", "code": 500}
