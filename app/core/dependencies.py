from fastapi import Depends
from app.core.security import get_current_user


def get_pagination(page: int = 1, page_size: int = 20):
    """分页参数依赖"""
    offset = (page - 1) * page_size
    return {"page": page, "page_size": page_size, "offset": offset}
