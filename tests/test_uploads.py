"""图片上传测试"""
import io
import pytest

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def make_image_bytes() -> bytes:
    if HAS_PIL:
        img = Image.new("RGB", (100, 100), color="red")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf.read()
    # 无 Pillow 时构造最小 PNG 头
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


@pytest.mark.asyncio
async def test_upload_image_success(client, auth_token):
    """测试成功上传图片"""
    img_bytes = make_image_bytes()
    response = await client.post(
        "/api/v1/uploads/image",
        headers=auth_token,
        files={"file": ("test.png", img_bytes, "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["url"].startswith("/uploads/")


@pytest.mark.asyncio
async def test_upload_image_invalid_type(client, auth_token):
    """测试上传非图片类型"""
    response = await client.post(
        "/api/v1/uploads/image",
        headers=auth_token,
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    data = response.json()
    assert data["code"] == 400


@pytest.mark.asyncio
async def test_upload_image_no_auth(client):
    """测试未登录上传"""
    img_bytes = make_image_bytes()
    response = await client.post(
        "/api/v1/uploads/image",
        files={"file": ("test.png", img_bytes, "image/png")},
    )
    assert response.status_code == 401
