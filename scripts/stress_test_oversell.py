"""
交易行锁防超卖压测脚本

模拟 5 个用户同时购买同一商品，验证 SELECT ... FOR UPDATE 行锁防止超卖。
预期结果：只有 1 个用户成功，其余 4 个收到"商品已下架或已预订"。
"""
import asyncio
import httpx
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

# 5 个学生账号
STUDENTS = [
    {"username": "student1", "password": "pass1123"},
    {"username": "student2", "password": "pass2123"},
    {"username": "student3", "password": "pass3123"},
    {"username": "student4", "password": "pass4123"},
    {"username": "student5", "password": "pass5123"},
]


async def login(client: httpx.AsyncClient, username: str, password: str) -> str:
    """登录获取 token"""
    resp = await client.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password},
    )
    data = resp.json()
    return data["data"]["token"]


async def buy_item(client: httpx.AsyncClient, token: str, item_id: int) -> dict:
    """发起购买请求"""
    resp = await client.post(
        f"{BASE_URL}/requests/",
        json={"item_id": item_id, "message": "我要买这个"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()


async def get_item_status(client: httpx.AsyncClient, token: str, item_id: int) -> int:
    """获取商品当前状态"""
    resp = await client.get(
        f"{BASE_URL}/items/{item_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = resp.json()
    return data["data"]["status"]


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        # 1. 登录获取 5 个学生的 token
        print("=" * 60)
        print("  交易行锁防超卖压测")
        print("=" * 60)

        tokens = []
        for s in STUDENTS:
            try:
                token = await login(client, s["username"], s["password"])
                tokens.append(token)
                print(f"  ✅ {s['username']} 登录成功")
            except Exception as e:
                print(f"  ❌ {s['username']} 登录失败: {e}")
                return

        # 2. 用 student1 的 token 查找一个在售商品（属于 admin）
        resp = await client.get(
            f"{BASE_URL}/items/?page=1&page_size=20",
            headers={"Authorization": f"Bearer {tokens[0]}"},
        )
        items = resp.json()["data"]["items"]
        # 选第一个在售商品
        target_item = items[0]
        item_id = target_item["item_id"]
        print(f"\n  目标商品: ID={item_id}, 标题={target_item['title']}, 状态={target_item['status']}")

        # 3. 5 个用户同时发起购买请求
        print(f"\n  🚀 5 个用户并发购买商品 #{item_id}...")
        start = time.time()
        results = await asyncio.gather(
            *[buy_item(client, token, item_id) for token in tokens],
            return_exceptions=True,
        )
        elapsed = (time.time() - start) * 1000

        # 4. 统计结果
        success_count = 0
        fail_count = 0
        print(f"\n  并发请求完成，耗时: {elapsed:.1f} ms")
        print("-" * 60)

        for i, (student, result) in enumerate(zip(STUDENTS, results)):
            if isinstance(result, Exception):
                print(f"  {student['username']}: ❌ 异常 - {result}")
                fail_count += 1
            elif result.get("code") == 200:
                print(f"  {student['username']}: ✅ 成功 - {result['data'].get('message', '')}")
                success_count += 1
            else:
                msg = result.get("message", "未知错误")
                print(f"  {student['username']}: ⚠️ 被拒 - {msg}")
                fail_count += 1

        print("-" * 60)
        print(f"\n  📊 结果: {success_count} 成功, {fail_count} 被拒")

        # 5. 验证商品状态
        final_status = await get_item_status(client, tokens[0], item_id)
        status_text = {0: "在售", 1: "已预订", 2: "已售出"}.get(final_status, "未知")
        print(f"  商品最终状态: {final_status} ({status_text})")

        # 6. 判定
        if success_count == 1 and final_status == 1:
            print("\n  ✅ 压测通过：行锁成功防止超卖，仅 1 个用户购买成功")
        elif success_count == 1:
            print(f"\n  ✅ 压测通过：仅 1 个用户成功（状态={status_text}）")
        else:
            print(f"\n  ❌ 压测异常：{success_count} 个用户成功（预期 1 个）")


if __name__ == "__main__":
    asyncio.run(main())
