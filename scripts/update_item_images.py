"""
更新商品图片 - 为每个商品生成与名称匹配的图片

使用 text_to_image API 生成商品图片，保存到 uploads/ 目录，
然后更新数据库 images 字段为本地路径。
"""
import asyncio
import sys
import os
import urllib.request
import urllib.parse
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from app.models.item import Item
from sqlalchemy import select

# 商品标题 → 图片生成 prompt 映射
ITEM_PROMPTS = {
    "高等数学第七版": "A college advanced mathematics textbook, seventh edition, blue cover with mathematical formulas, Chinese university textbook, product photography on white background",
    "线性代数同步辅导": "A linear algebra study guide book, green cover with matrix illustrations, Chinese textbook, product photography on white background",
    "考研英语真题汇编": "A collection of English exam papers for graduate entrance exam, red cover, thick book, Chinese study material, product photography on white background",
    "MacBook Pro 2019": "MacBook Pro 2019 16 inch laptop, silver aluminum body, open showing desktop, Apple laptop, product photography on clean white background",
    "小米手环7": "Xiaomi Mi Band 7 smart bracelet, black fitness tracker with rectangular screen, wearable device, product photography on white background",
    "AirPods Pro 一代": "Apple AirPods Pro first generation wireless earbuds, white charging case open, earbuds visible, product photography on white background",
    "罗技无线鼠标": "Logitech M590 wireless mouse, dark gray, multi-device switching, computer mouse, product photography on white background",
    "LED护眼台灯": "LED desk lamp, white, three brightness levels, USB powered, modern design, study lamp, product photography on white background",
    "膳魔师保温杯": "Thermos stainless steel vacuum insulated water bottle, 500ml, silver, thermos flask, product photography on white background",
    "宿舍收纳箱": "Plastic storage box with drawers, three tiers, transparent, dormitory organizer, product photography on white background",
    "优衣库羽绒服": "Uniqlo down jacket, mens L size, black, winter coat, product photography on white background",
    "Nike跑步鞋": "Nike running shoes, mens size 42, white with red swoosh, athletic sneakers, product photography on white background",
    "斯伯丁篮球": "Spalding basketball, orange, 74-604 model, outdoor basketball, product photography on white background",
    "瑜伽垫": "Yoga mat, TPE material, 6mm thick, purple, rolled up, exercise mat, product photography on white background",
    "LAMY钢笔": "LAMY Safari fountain pen, yellow, F nib, German pen, stationery, product photography on white background",
    "百乐中性笔套装": "Pilot gel pen set, 0.5mm, 10 pieces, black, stationery set, product photography on white background",
}


async def download_image(prompt: str, save_path: str, image_size: str = "landscape_4_3"):
    """调用 text_to_image API 下载图片"""
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt={encoded_prompt}&image_size={image_size}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=60) as resp:
            if resp.status == 200:
                data = resp.read()
                with open(save_path, "wb") as f:
                    f.write(data)
                return True
            else:
                print(f"  ❌ HTTP {resp.status}")
                return False
    except Exception as e:
        print(f"  ❌ 下载失败: {e}")
        return False


async def main():
    db_manager.ensure_initialized()
    session_factory = db_manager._session_factories[db_manager.get_active_db_type()]
    session = session_factory()

    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    print("=" * 60)
    print("  商品图片更新工具")
    print(f"  数据库: {db_manager.get_active_db_type().value}")
    print("=" * 60)

    result = await session.execute(select(Item).order_by(Item.item_id))
    items = result.scalars().all()

    print(f"\n  共 {len(items)} 个商品需要更新图片\n")

    updated = 0
    for item in items:
        prompt = ITEM_PROMPTS.get(item.title)
        if not prompt:
            print(f"  ⏭️  跳过 #{item.item_id} {item.title}（无 prompt 映射）")
            continue

        # 用商品 ID 作为文件名，确保唯一
        filename = f"item_{item.item_id}.png"
        save_path = os.path.join(upload_dir, filename)

        # 如果图片已存在，跳过下载
        if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
            print(f"  ✅ #{item.item_id} {item.title} - 图片已存在，跳过下载")
        else:
            print(f"  🔄 #{item.item_id} {item.title} - 生成图片中...")
            success = await download_image(prompt, save_path)
            if not success:
                print(f"  ⚠️  下载失败，保留旧图片")
                continue
            print(f"  ✅ 已保存: {filename}")

        # 更新数据库
        item.images = f"/uploads/{filename}"
        await session.flush()
        updated += 1

    await session.commit()
    await session.close()
    await db_manager.close_all()

    print(f"\n  📊 更新完成: {updated}/{len(items)} 个商品")
    print(f"  图片保存在: {upload_dir}")


if __name__ == "__main__":
    asyncio.run(main())
