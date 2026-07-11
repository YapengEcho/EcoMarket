"""add indexes for category_id status_price parent_id and fulltext title

Revision ID: aa74f667772e
Revises: 888a6685f76f
Create Date: 2026-07-11 16:07:40.925351

索引优化:
- idx_category_id: items.category_id 普通索引，优化分类筛选
- idx_status_price: items.(status, price) 联合索引，优化价格区间搜索
- idx_parent_id: categories.parent_id 索引，优化递归分类统计
- ft_title: items.title FULLTEXT 全文索引（MySQL 专用），优化全文搜索
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'aa74f667772e'
down_revision: Union[str, None] = '888a6685f76f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加索引"""
    # 普通索引：优化分类筛选查询
    op.create_index('idx_category_id', 'items', ['category_id'], unique=False)

    # 联合索引：优化价格区间搜索
    op.create_index('idx_status_price', 'items', ['status', 'price'], unique=False)

    # 普通索引：优化递归分类统计
    op.create_index('idx_parent_id', 'categories', ['parent_id'], unique=False)

    # FULLTEXT 全文索引（MySQL 专用，用原生 SQL 创建）
    bind = op.get_bind()
    if bind.dialect.name == 'mysql':
        bind.execute(sa.text("CREATE FULLTEXT INDEX ft_title ON items(title)"))


def downgrade() -> None:
    """删除索引"""
    bind = op.get_bind()
    if bind.dialect.name == 'mysql':
        bind.execute(sa.text("DROP INDEX ft_title ON items"))

    op.drop_index('idx_parent_id', table_name='categories')
    op.drop_index('idx_status_price', table_name='items')
    op.drop_index('idx_category_id', table_name='items')
