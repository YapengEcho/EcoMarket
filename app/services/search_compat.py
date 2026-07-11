"""
数据库搜索兼容层

不同数据库的全文搜索语法不同:
- MySQL:  MATCH(title) AGAINST(:keyword)
- PostgreSQL/openGauss: to_tsvector('english', title) @@ to_tsquery('english', :keyword)
- SQLite: LIKE (降级方案)

本模块根据当前活跃数据库类型返回合适的搜索条件。
"""
from sqlalchemy import text, or_, String
from sqlalchemy.sql import operators
from app.core.database import DBType, db_manager
from app.models.item import Item
import logging

logger = logging.getLogger(__name__)


def build_keyword_condition(keyword: str):
    """根据当前数据库类型构建关键词搜索条件

    注意: MySQL 默认 FULLTEXT 解析器不支持中文分词，搜索中文时返回空结果。
    因此搜索统一使用 LIKE（配合 idx_status_time_cover 覆盖索引仍高效），
    FULLTEXT 索引仅在 /items/explain 演示接口中展示。
    """
    # 统一使用 LIKE 搜索，兼容中英文
    return Item.title.like(f"%{keyword}%")


def build_explain_sql(keyword: str, db_type: DBType) -> str:
    """返回对应数据库的 EXPLAIN SQL（用于演示索引优化效果）"""
    if db_type == DBType.MYSQL:
        return """
            EXPLAIN SELECT * FROM items
            WHERE status = 0 AND MATCH(title) AGAINST(:keyword)
            ORDER BY created_at DESC
        """
    elif db_type == DBType.OPENGUASS:
        return """
            EXPLAIN ANALYZE
            SELECT * FROM items
            WHERE status = 0 AND to_tsvector('english', title) @@ to_tsquery('english', :keyword)
            ORDER BY created_at DESC
        """
    else:
        # SQLite 的 EXPLAIN QUERY PLAN
        return """
            EXPLAIN QUERY PLAN
            SELECT * FROM items
            WHERE status = 0 AND title LIKE :keyword
            ORDER BY created_at DESC
        """
