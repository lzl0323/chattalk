"""
推荐问题 API 路由
提供智能推荐问题生成接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from ..core.database import get_db
from ..core.auth import get_current_user
from ..models.db_models import User
from ..services.suggestion_service import SuggestionService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/suggestions", tags=["推荐问题"])


class Suggestion(BaseModel):
    """推荐问题模型"""
    type: str  # trending, research, personalized, general
    title: str
    icon: str = "bolt"


class SuggestionsResponse(BaseModel):
    """推荐问题响应"""
    suggestions: List[Suggestion]


@router.get("/", response_model=SuggestionsResponse, summary="获取推荐问题")
async def get_suggestions(
    count: int = Query(6, ge=1, le=10, description="推荐问题数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取智能推荐问题（自动保存到数据库，避免重复推荐）
    
    - 基于用户最近的聊天主题
    - 结合当前技术热点
    - 融合科研前沿趋势
    - 避免重复最近7天推荐过的内容
    - 保存推荐记录用于统计分析
    
    返回 JSON 格式的推荐问题列表
    """
    try:
        # 生成推荐（已优化为使用后备推荐，快速且避免重复）
        suggestions = await SuggestionService.get_fallback_suggestions(
            db=db,
            user_id=current_user.id,
            count=count
        )
        
        # 保存推荐记录到数据库
        await SuggestionService.save_suggestions(
            db=db,
            user_id=current_user.id,
            suggestions=suggestions
        )
        
        return SuggestionsResponse(suggestions=suggestions)
        
    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}", exc_info=True)
        # 返回后备推荐（不保存）
        fallback = await SuggestionService.get_fallback_suggestions(count=count)
        return SuggestionsResponse(suggestions=fallback)


@router.get("/fallback", response_model=SuggestionsResponse, summary="获取后备推荐问题")
async def get_fallback_suggestions(
    count: int = Query(6, ge=1, le=10, description="推荐问题数量")
):
    """
    获取后备推荐问题（不需要认证）
    
    当 AI 生成失败或用户未登录时使用
    """
    suggestions = SuggestionService.get_fallback_suggestions(count)
    return SuggestionsResponse(suggestions=suggestions)
