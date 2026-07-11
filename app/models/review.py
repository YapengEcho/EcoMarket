from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Index, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    request_id = Column(BigInteger, ForeignKey("requests.request_id"), nullable=False)
    reviewer_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    reviewee_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_reviewee", "reviewee_id"),
        Index("idx_request_id", "request_id"),
    )
