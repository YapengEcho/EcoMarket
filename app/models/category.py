from sqlalchemy import Column, Integer, String, Index
from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)

    __table_args__ = (
        Index("idx_parent_id", "parent_id"),
    )
