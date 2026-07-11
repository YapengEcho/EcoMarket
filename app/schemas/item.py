from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    category_id: Optional[int] = None
    condition: int = 0
    images: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    category_id: Optional[int] = None
    condition: Optional[int] = None
    status: Optional[int] = None
    images: Optional[str] = None


class ItemResponse(BaseModel):
    item_id: int
    user_id: int
    category_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    condition: int
    status: int
    images: Optional[List[str]] = None
    view_count: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ItemSearchParams(BaseModel):
    keyword: Optional[str] = None
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    status: int = 0
    page: int = 1
    page_size: int = 20
