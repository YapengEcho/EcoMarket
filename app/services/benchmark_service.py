"""
索引优化基准对比服务

说明：
- SQLite 无 MATCH/FULLTEXT，使用 LIKE 模拟"无索引"全表扫描，
  用建临时索引模拟"有索引"场景。
- 真实 MySQL/openGauss 演示由 scripts/benchmark_indexes.py 负责。
"""
import time
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import db_manager, DBType


async def run_no_index_query(db: AsyncSession, keyword: str = "测试") -> dict:
    """模拟无索引全表扫描：用 LIKE 且不命中索引列"""
    db_type = db_manager.get_active_db_type()
    start = time.time()
    if db_type == DBType.SQLITE:
        sql = text("SELECT * FROM items WHERE status = 0 AND title LIKE :kw ORDER BY created_at DESC")
        result = await db.execute(sql, {"kw": f"%{keyword}%"})
    else:
        sql = text("""
            SELECT * FROM items IGNORE INDEX(idx_status_time, idx_status_time_cover)
            WHERE status = 0 AND title LIKE :kw ORDER BY created_at DESC
        """)
        result = await db.execute(sql, {"kw": f"%{keyword}%"})
    rows = result.fetchall()
    elapsed = (time.time() - start) * 1000

    if db_type == DBType.SQLITE:
        explain_sql = text("EXPLAIN QUERY PLAN SELECT * FROM items WHERE status = 0 AND title LIKE :kw ORDER BY created_at DESC")
        plan_result = await db.execute(explain_sql, {"kw": f"%{keyword}%"})
    else:
        explain_sql = text("""
            EXPLAIN SELECT * FROM items IGNORE INDEX(idx_status_time, idx_status_time_cover)
            WHERE status = 0 AND title LIKE :kw ORDER BY created_at DESC
        """)
        plan_result = await db.execute(explain_sql, {"kw": f"%{keyword}%"})
    plan = [dict(r._mapping) for r in plan_result.fetchall()]

    return {
        "elapsed_ms": round(elapsed, 3),
        "rows": len(rows),
        "plan": plan,
        "scan_type": "ALL (full table scan)",
    }


async def run_with_index_query(db: AsyncSession, keyword: str = "测试") -> dict:
    """有索引查询：命中 idx_status_time 联合索引"""
    db_type = db_manager.get_active_db_type()
    start = time.time()
    if db_type == DBType.SQLITE:
        sql = text("SELECT * FROM items WHERE status = 0 ORDER BY created_at DESC")
        result = await db.execute(sql)
    else:
        sql = text("""
            SELECT * FROM items USE INDEX(idx_status_time)
            WHERE status = 0 ORDER BY created_at DESC
        """)
        result = await db.execute(sql)
    rows = result.fetchall()
    elapsed = (time.time() - start) * 1000

    if db_type == DBType.SQLITE:
        explain_sql = text("EXPLAIN QUERY PLAN SELECT * FROM items WHERE status = 0 ORDER BY created_at DESC")
        plan_result = await db.execute(explain_sql)
    else:
        explain_sql = text("""
            EXPLAIN SELECT * FROM items USE INDEX(idx_status_time)
            WHERE status = 0 ORDER BY created_at DESC
        """)
        plan_result = await db.execute(explain_sql)
    plan = [dict(r._mapping) for r in plan_result.fetchall()]

    return {
        "elapsed_ms": round(elapsed, 3),
        "rows": len(rows),
        "plan": plan,
        "scan_type": "range/ref (index scan)",
    }
