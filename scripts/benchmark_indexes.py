"""
索引优化演示脚本（MySQL 真实环境运行）

用法（需先配置 MySQL）:
  1. 设置 .env: DB_STRATEGY=primary
  2. python scripts/benchmark_indexes.py

输出：无索引 vs 有索引 的 EXPLAIN 与耗时对比
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from app.services.benchmark_service import run_no_index_query, run_with_index_query


async def main():
    db_manager.ensure_initialized()
    session_factory = db_manager._session_factories[db_manager.get_active_db_type()]
    session = session_factory()

    print("=" * 60)
    print("  EcoMarket 索引优化基准对比")
    print(f"  当前数据库: {db_manager.get_active_db_type().value}")
    print("=" * 60)

    print("\n【优化前 - 无索引全表扫描】")
    before = await run_no_index_query(session)
    print(f"  耗时: {before['elapsed_ms']} ms")
    print(f"  扫描类型: {before['scan_type']}")
    print(f"  返回行数: {before['rows']}")
    print(f"  EXPLAIN:")
    for row in before["plan"]:
        print(f"    {row}")

    print("\n【优化后 - 联合索引扫描】")
    after = await run_with_index_query(session)
    print(f"  耗时: {after['elapsed_ms']} ms")
    print(f"  扫描类型: {after['scan_type']}")
    print(f"  返回行数: {after['rows']}")
    print(f"  EXPLAIN:")
    for row in after["plan"]:
        print(f"    {row}")

    speedup = (before["elapsed_ms"] / after["elapsed_ms"]) if after["elapsed_ms"] > 0 else 0
    print(f"\n【性能提升】{speedup:.2f} 倍")

    await session.close()
    await db_manager.close_all()


if __name__ == "__main__":
    asyncio.run(main())
