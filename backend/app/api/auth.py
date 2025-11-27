"""用户认证 API"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from ..core.database import get_db
from ..core.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    get_current_user
)
from ..models.db_models import User
from ..models.schemas import (
    UserRegister, 
    UserLogin, 
    Token, 
    UserResponse,
    ApiResponse
)
from ..core.config import settings

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=Token, summary="用户注册")
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    
    - **email**: 用户邮箱（唯一）
    - **password**: 密码（6-100字符，将被哈希存储）
    
    返回：JWT Token 和用户信息
    """
    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # 生成 JWT Token
    access_token = create_access_token(
        data={"user_id": new_user.id, "email": new_user.email}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(new_user)
    )


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    
    - **email**: 用户邮箱
    - **password**: 密码
    
    返回：JWT Token 和用户信息
    """
    # 查找用户
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )
    
    # 验证密码
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )
    
    # 生成 JWT Token
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户的信息
    
    需要提供有效的 Bearer Token
    """
    return UserResponse.from_orm(current_user)


@router.post("/logout", response_model=ApiResponse, summary="用户登出")
async def logout(current_user: User = Depends(get_current_user)):
    """
    用户登出
    
    注意：JWT 是无状态的，实际上前端只需要删除本地存储的 token 即可
    此接口主要用于日志记录和未来可能的 token 黑名单功能
    """
    return ApiResponse(
        code=200,
        message="登出成功",
        data={"email": current_user.email}
    )
