"""
数据库初始化脚本 - 创建表结构并插入种子数据

用法: python -m scripts.init_data  或  python scripts/init_data.py
"""
import asyncio
import sys
import os

# 添加项目根目录到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager, Base, DBType
from app.core.security import hash_password
from app.models.user import User
from app.models.item import Item
from app.models.category import Category
from app.models.request import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def init_db():
    """初始化数据库表结构"""
    db_manager.ensure_initialized()
    engine = db_manager._engines[db_manager.get_active_db_type()]

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表结构创建完成")


async def seed_data():
    """插入种子数据"""
    db_manager.ensure_initialized()
    session_factory = db_manager._session_factories[db_manager.get_active_db_type()]
    session = session_factory()

    try:
        # 检查是否已有数据
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("⚠️ 数据库已有数据，跳过种子数据插入")
            return

        # 1. 创建管理员用户
        admin = User(
            username="admin",
            password_hash=hash_password("admin123"),
            email="admin@ecomarket.edu",
            school="测试大学",
            is_admin=True,
            reputation_score=5.00,
        )
        session.add(admin)
        await session.flush()
        print(f"  ✅ 创建管理员: admin/admin123 (ID: {admin.user_id})")

        # 2. 创建测试用户
        test_users = []
        user_profiles = [
            ("student1", "pass1123", "清华大学", "s1@edu.cn"),
            ("student2", "pass2123", "北京大学", "s2@edu.cn"),
            ("student3", "pass3123", "复旦大学", "s3@edu.cn"),
            ("student4", "pass4123", "浙江大学", "s4@edu.cn"),
            ("student5", "pass5123", "上海交大", "s5@edu.cn"),
        ]
        for uname, pwd, school, email in user_profiles:
            user = User(
                username=uname,
                password_hash=hash_password(pwd),
                email=email,
                school=school,
                reputation_score=5.00,
            )
            session.add(user)
            test_users.append(user)
            await session.flush()
            print(f"  ✅ 创建用户: {uname}/{pwd} (ID: {user.user_id})")

        # 3. 创建分类
        categories_data = [
            ("教材书籍", 0, 1),
            ("电子数码", 0, 2),
            ("生活用品", 0, 3),
            ("服装鞋帽", 0, 4),
            ("运动器材", 0, 5),
            ("文具用品", 0, 6),
        ]
        categories = []
        for name, parent, order in categories_data:
            cat = Category(name=name, parent_id=parent, sort_order=order)
            session.add(cat)
            categories.append(cat)
        await session.flush()
        print(f"  ✅ 创建 {len(categories)} 个商品分类")

        # 4. 创建测试商品（含真实图片URL）
        items_data = [
            # 教材书籍
            ("高等数学第七版", "同济大学版，九成新，无笔记。考研复习用书，重点知识点已标注。", 25.00, 49.80, 0, 0,
             "https://picsum.photos/seed/book1/600/450"),
            ("线性代数同步辅导", "清华版，有少量铅笔笔记，可擦除。配套习题解答完整。", 15.00, 35.00, 0, 0,
             "https://picsum.photos/seed/book2/600/450"),
            ("考研英语真题汇编", "2015-2024年全套，无答案缺失，解析详细。", 30.00, 120.00, 0, 0,
             "https://picsum.photos/seed/book3/600/450"),
            # 电子数码
            ("MacBook Pro 2019", "16寸，32G内存，512G SSD，无磕碰，电池循环98次。", 6500.00, 18999.00, 1, 0,
             "https://picsum.photos/seed/laptop1/600/450"),
            ("小米手环7", "几乎全新，带原装充电线，功能正常。", 120.00, 249.00, 1, 0,
             "https://picsum.photos/seed/band1/600/450"),
            ("AirPods Pro 一代", "左耳有轻微划痕，降噪功能完好，带原装盒。", 450.00, 1599.00, 1, 1,
             "https://picsum.photos/seed/airpods1/600/450"),
            ("罗技无线鼠标", "M590，多设备切换，使用半年，成色佳。", 65.00, 199.00, 1, 0,
             "https://picsum.photos/seed/mouse1/600/450"),
            # 生活用品
            ("LED护眼台灯", "三档调光，USB供电，宿舍神器，无划痕。", 35.00, 89.00, 2, 0,
             "https://picsum.photos/seed/lamp1/600/450"),
            ("膳魔师保温杯", "500ml，不锈钢内胆，无划痕，保温效果一流。", 40.00, 199.00, 2, 0,
             "https://picsum.photos/seed/cup1/600/450"),
            ("宿舍收纳箱", "三层抽屉式，塑料材质，搬家用了一学期。", 28.00, 79.00, 2, 1,
             "https://picsum.photos/seed/box1/600/450"),
            # 服装鞋帽
            ("优衣库羽绒服", "男款L码，黑色，去年冬买的，洗过两次。", 150.00, 499.00, 3, 0,
             "https://picsum.photos/seed/coat1/600/450"),
            ("Nike跑步鞋", "男款42码，白色，穿过几次，鞋底无磨损。", 180.00, 599.00, 3, 0,
             "https://picsum.photos/seed/shoe1/600/450"),
            # 运动器材
            ("斯伯丁篮球", "74-604，室外打了一学期，手感依然很好。", 80.00, 199.00, 4, 0,
             "https://picsum.photos/seed/ball1/600/450"),
            ("瑜伽垫", "TPE材质，6mm加厚，防滑，几乎全新。", 45.00, 129.00, 4, 0,
             "https://picsum.photos/seed/yoga1/600/450"),
            # 文具用品
            ("LAMY钢笔", "Safari系列，黄色，F尖，闲置中。", 75.00, 168.00, 5, 0,
             "https://picsum.photos/seed/pen1/600/450"),
            ("百乐中性笔套装", "0.5mm，10支装，黑色，全新未拆封。", 18.00, 45.00, 5, 0,
             "https://picsum.photos/seed/pen2/600/450"),
        ]

        items = []
        for i, (title, desc, price, orig, cat_idx, condition, img) in enumerate(items_data):
            user = test_users[i % len(test_users)]
            # 让部分商品已售出/已预订
            status = 0
            if i == 5:  # AirPods 已预订
                status = 1
            elif i == 9:  # 收纳箱已售
                status = 2
            item = Item(
                user_id=user.user_id,
                category_id=categories[cat_idx].category_id,
                title=title,
                description=desc,
                price=price,
                original_price=orig,
                condition=condition,
                status=status,
                images=img,
                view_count=(i + 1) * 7,
            )
            session.add(item)
            items.append(item)
        await session.flush()
        print(f"  ✅ 创建 {len(items_data)} 个测试商品（含真实图片URL）")

        # 5. 创建交易记录
        # student2 向 student1 买高数书（已预订）
        r1 = Request(
            item_id=items[0].item_id,
            requester_id=test_users[1].user_id,
            seller_id=test_users[0].user_id,
            status=1,
            message="书还在吗？能否便宜5块？",
        )
        # student3 向 student2 买收纳箱（已完成）
        r2 = Request(
            item_id=items[9].item_id,
            requester_id=test_users[2].user_id,
            seller_id=test_users[1].user_id,
            status=3,
            message="明天下午可以面交吗？三食堂门口。",
        )
        # student4 向 student3 买鼠标（待处理）
        r3 = Request(
            item_id=items[6].item_id,
            requester_id=test_users[3].user_id,
            seller_id=test_users[2].user_id,
            status=0,
            message="鼠标还能用吗？有没有按键失灵？",
        )
        # student5 向 student1 买瑜伽垫（已接受）
        r4 = Request(
            item_id=items[13].item_id,
            requester_id=test_users[4].user_id,
            seller_id=test_users[0].user_id,
            status=1,
            message="瑜伽垫在哪面交？",
        )
        for r in [r1, r2, r3, r4]:
            session.add(r)
        await session.flush()
        print(f"  ✅ 创建 4 条交易记录（待处理/已接受/已完成）")

        await session.commit()
        print("\n✅ 种子数据插入完成!")
        print("\n📋 测试账号:")
        print("  管理员: admin / admin123")
        print("  学生:   student1 / pass1123")
        print("  学生:   student2 / pass2123")
        print("  学生:   student3 / pass3123")
        print("  学生:   student4 / pass4123")
        print("  学生:   student5 / pass5123")

    except Exception as e:
        await session.rollback()
        print(f"❌ 种子数据插入失败: {e}")
        raise
    finally:
        await session.close()


async def main():
    print("=" * 60)
    print(f"  EcoMarket 数据库初始化工具")
    print(f"  数据库策略: {db_manager.get_active_db_type().value if db_manager._initialized else 'pending'}")
    print("=" * 60)

    await init_db()
    await seed_data()

    await db_manager.close_all()
    print("\n✅ 全部完成!")


if __name__ == "__main__":
    asyncio.run(main())
