from pydantic import BaseModel
from typing import Optional


class CategoryCreate(BaseModel):
    name: str
    parent_id: int = 0
    sort_order: int = 0


class CategoryResponse(BaseModel):
    category_id: int
    name: str
    parent_id: int
    sort_order: int

    class Config:
        from_attributes = True
