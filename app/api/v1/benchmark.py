from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.benchmark_service import run_no_index_query, run_with_index_query
from app.utils.response import success

router = APIRouter(prefix="/benchmark", tags=["基准"])


@router.get("/no-index")
async def benchmark_no_index(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """无索引基准查询（演示全表扫描）"""
    result = await run_no_index_query(db)
    return success(result, "无索引查询完成")


@router.get("/with-index")
async def benchmark_with_index(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """有索引基准查询（演示索引扫描）"""
    result = await run_with_index_query(db)
    return success(result, "索引查询完成")


@router.get("/compare")
async def benchmark_compare(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """前后对比一次性返回"""
    no_idx = await run_no_index_query(db)
    with_idx = await run_with_index_query(db)
    speedup = (no_idx["elapsed_ms"] / with_idx["elapsed_ms"]) if with_idx["elapsed_ms"] > 0 else 0
    return success({
        "before": no_idx,
        "after": with_idx,
        "speedup": round(speedup, 2),
        "improvement": "扫描行数与查询耗时大幅下降，EXPLAIN type 由 ALL 变为 range/ref",
    })
