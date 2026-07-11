"""
清理数据库 - 删除所有商品、用户、消息、交易、评价、收藏
仅保留 admin 管理员账户
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from sqlalchemy import text


async def main():
    db_manager.ensure_initialized()
    engine = db_manager._engines[db_manager.get_active_db_type()]

    print("=" * 60)
    print("  数据库清理工具")
    print(f"  数据库: {db_manager.get_active_db_type().value}")
    print("=" * 60)

    async with engine.begin() as conn:
        # 按外键依赖顺序删除
        tables = ["favorites", "reviews", "messages", "requests", "items"]
        for table in tables:
            result = await conn.execute(text(f"DELETE FROM {table}"))
            print(f"  ✅ 清空 {table}: 删除 {result.rowcount} 行")

        # 删除除 admin 外的所有用户
        result = await conn.execute(
            text("DELETE FROM users WHERE username != 'admin'")
        )
        print(f"  ✅ 清空 users (保留 admin): 删除 {result.rowcount} 行")

    # 重置 admin 的信誉分
    async with engine.begin() as conn:
        await conn.execute(
            text("UPDATE users SET reputation_score = 5.00 WHERE username = 'admin'")
        )
        print("  ✅ 重置 admin 信誉分为 5.00")

    # 查看剩余数据
    async with engine.connect() as conn:
        for table in ["users", "items", "categories", "requests", "messages", "reviews", "favorites"]:
            result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"  📊 {table}: {count} 行")

    await db_manager.close_all()
    print("\n✅ 清理完成！仅保留 admin 管理员")


if __name__ == "__main__":
    asyncio.run(main())
