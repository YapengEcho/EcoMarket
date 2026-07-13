from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.utils.response import success, error
from app.schemas.user import UserCreate, UserLogin, UserUpdate

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register")
async def register(req: UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    result = await db.execute(select(User).where(User.username == req.username))
    if result.scalar_one_or_none():
        return error("用户名已存在", 400)

    # 空字符串转 None，避免 UNIQUE 约束冲突（多个空字符串被视为重复值）
    email = req.email.strip() if req.email else None
    phone = req.phone.strip() if req.phone else None
    school = req.school.strip() if req.school else None

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        email=email or None,
        phone=phone or None,
        school=school or None,
        reputation_score=5.00,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return success({"user_id": user.user_id, "username": user.username}, "注册成功")


@router.post("/login")
async def login(req: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        return error("用户名或密码错误", 401)

    if not user.is_active:
        return error("账号已被禁用，请联系管理员", 403)

    token = create_access_token({"user_id": user.user_id, "username": user.username})
    return success({"token": token, "user_id": user.user_id, "username": user.username})


@router.get("/me")
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户信息"""
    result = await db.execute(select(User).where(User.user_id == current_user["user_id"]))
    user = result.scalar_one_or_none()
    if not user:
        return error("用户不存在", 404)

    return success({
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "avatar": user.avatar,
        "school": user.school,
        "reputation_score": float(user.reputation_score) if user.reputation_score else 5.0,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    })


@router.put("/me")
async def update_profile(
    req: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新个人信息"""
    result = await db.execute(select(User).where(User.user_id == current_user["user_id"]))
    user = result.scalar_one_or_none()
    if not user:
        return error("用户不存在", 404)

    if req.email is not None:
        user.email = req.email
    if req.phone is not None:
        user.phone = req.phone
    if req.avatar is not None:
        user.avatar = req.avatar
    if req.school is not None:
        user.school = req.school

    await db.commit()
    return success({"user_id": user.user_id}, "更新成功")
