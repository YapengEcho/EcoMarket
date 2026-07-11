"""管理员模块测试"""
import pytest


@pytest.mark.asyncio
async def test_admin_list_users(client, auth_token):
    """管理员获取用户列表（auth_token 对应 user_id=1，即管理员）"""
    response = await client.get("/api/v1/admin/users", headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]) >= 1


@pytest.mark.asyncio
async def test_admin_list_users_forbidden(client, auth_token, second_token):
    """非管理员无权访问（auth_token 创建 user_id=1 管理员，second_token 对应 user_id=2）"""
    response = await client.get("/api/v1/admin/users", headers=second_token)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_audit_item(client, auth_token, seed_item):
    """管理员下架商品（审核）"""
    response = await client.put(
        f"/api/v1/admin/items/{seed_item.item_id}/audit",
        params={"status": 3},
        headers=auth_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["status"] == 3


@pytest.mark.asyncio
async def test_admin_stats(client, auth_token, seed_item):
    """管理员平台统计"""
    response = await client.get("/api/v1/admin/stats", headers=auth_token)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "total_users" in data["data"]
    assert "total_items" in data["data"]
