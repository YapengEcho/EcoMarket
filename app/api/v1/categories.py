from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category
from app.core.database import get_db
from app.utils.response import success, error
from app.schemas.category import CategoryCreate

router = APIRouter(prefix="/categories", tags=["分类"])


@router.get("/")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """获取所有分类"""
    result = await db.execute(
        select(Category).order_by(Category.sort_order, Category.category_id)
    )
    categories = result.scalars().all()
    return success([
        {
            "category_id": c.category_id,
            "name": c.name,
            "parent_id": c.parent_id,
            "sort_order": c.sort_order,
        }
        for c in categories
    ])


@router.post("/")
async def create_category(
    cat: CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建分类"""
    category = Category(name=cat.name, parent_id=cat.parent_id, sort_order=cat.sort_order)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return success({"category_id": category.category_id}, "分类创建成功")


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    name: str = None,
    db: AsyncSession = Depends(get_db),
):
    """更新分类"""
    result = await db.execute(select(Category).where(Category.category_id == category_id))
    cat = result.scalar_one_or_none()
    if not cat:
        return error("分类不存在", 404)
    if name is not None:
        cat.name = name
    await db.commit()
    return success({"category_id": category_id}, "更新成功")


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除分类"""
    result = await db.execute(select(Category).where(Category.category_id == category_id))
    cat = result.scalar_one_or_none()
    if not cat:
        return error("分类不存在", 404)
    await db.delete(cat)
    await db.commit()
    return success({"category_id": category_id}, "已删除")
