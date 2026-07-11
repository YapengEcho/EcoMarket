from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.review import Review
from app.core.database import get_db
from app.core.security import get_current_user
from app.utils.response import success, error
from app.schemas.review import ReviewCreate
from app.services import request_service

router = APIRouter(prefix="/reviews", tags=["评价"])


@router.post("/")
async def create_review(
    req: ReviewCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建评价"""
    result = await request_service.create_review(
        db=db,
        request_id=req.request_id,
        reviewer_id=current_user["user_id"],
        rating=req.rating,
        comment=req.comment,
    )

    if result.get("error"):
        return error(result["error"], result.get("code", 500))
    return success({"review_id": result.get("review_id")}, result.get("message", "评价成功"))


@router.get("/user/{user_id}")
async def get_user_reviews(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取用户收到的评价"""
    result = await db.execute(
        select(Review)
        .where(Review.reviewee_id == user_id)
        .order_by(Review.created_at.desc())
    )
    reviews = result.scalars().all()
    return success([
        {
            "review_id": r.review_id,
            "reviewer_id": r.reviewer_id,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reviews
    ])
