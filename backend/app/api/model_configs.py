"""
模型配置 API 路由
提供模型配置的增删改查和配额管理
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..core.database import get_db
from ..core.auth import get_current_user
from ..models.db_models import User, ModelConfig
from ..models.schemas import (
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigOut,
    ModelConfigList,
    QuotaResetRequest
)
from ..services.model_config_service import ModelConfigService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/model-configs", tags=["模型配置"])


@router.post("/", response_model=ModelConfigOut, summary="创建模型配置")
async def create_model_config(
    data: ModelConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新的模型配置
    
    - **name**: 模型展示名称（必须唯一）
    - **model**: 模型标识，如 gpt-4, deepseek-chat
    - **api_base**: API 地址
    - **api_key**: API Key（明文，会自动加密存储）
    - **description**: 模型描述（可选）
    - **quota_limit**: 配额限制（tokens）
    - **quota_reset_cron**: 配额重置 Cron 表达式（可选）
    
    需要用户认证。
    """
    try:
        config = await ModelConfigService.create_model_config(db, data)
        return ModelConfigService.to_output_schema(config)
    except Exception as e:
        logger.error(f"Failed to create model config: {e}")
        raise HTTPException(status_code=500, detail=f"创建模型配置失败: {str(e)}")


@router.get("/", response_model=ModelConfigList, summary="获取模型配置列表")
async def get_model_configs(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    active_only: bool = Query(False, description="是否只返回激活的模型"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取模型配置列表
    
    - **skip**: 跳过数量（分页）
    - **limit**: 限制数量（分页）
    - **active_only**: 是否只返回激活的模型
    
    返回配置列表和总数。需要用户认证。
    """
    try:
        configs, total = await ModelConfigService.get_model_configs(
            db, skip=skip, limit=limit, active_only=active_only
        )
        
        items = [ModelConfigService.to_output_schema(config) for config in configs]
        
        return ModelConfigList(total=total, items=items)
    except Exception as e:
        logger.error(f"Failed to get model configs: {e}")
        raise HTTPException(status_code=500, detail=f"获取模型配置列表失败: {str(e)}")


@router.get("/{config_id}", response_model=ModelConfigOut, summary="获取单个模型配置")
async def get_model_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个模型配置
    
    - **config_id**: 配置 ID
    
    需要用户认证。
    """
    config = await ModelConfigService.get_model_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    return ModelConfigService.to_output_schema(config)


@router.put("/{config_id}", response_model=ModelConfigOut, summary="更新模型配置")
async def update_model_config(
    config_id: int,
    data: ModelConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新模型配置
    
    - **config_id**: 配置 ID
    - 其他字段可选更新
    
    需要用户认证。
    """
    try:
        config = await ModelConfigService.update_model_config(db, config_id, data)
        if not config:
            raise HTTPException(status_code=404, detail="模型配置不存在")
        
        return ModelConfigService.to_output_schema(config)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update model config: {e}")
        raise HTTPException(status_code=500, detail=f"更新模型配置失败: {str(e)}")


@router.delete("/{config_id}", summary="删除模型配置")
async def delete_model_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除模型配置
    
    - **config_id**: 配置 ID
    
    需要用户认证。
    """
    success = await ModelConfigService.delete_model_config(db, config_id)
    if not success:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    return {"message": "模型配置已删除", "id": config_id}


@router.post("/{config_id}/reset-quota", response_model=ModelConfigOut, summary="重置配额")
async def reset_quota(
    config_id: int,
    data: QuotaResetRequest = QuotaResetRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    重置模型配额
    
    - **config_id**: 配置 ID
    - **quota_used**: 重置后的使用量（默认 0）
    
    重置配额后会自动激活模型。需要用户认证。
    """
    try:
        config = await ModelConfigService.reset_quota(db, config_id, data.quota_used)
        if not config:
            raise HTTPException(status_code=404, detail="模型配置不存在")
        
        return ModelConfigService.to_output_schema(config)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset quota: {e}")
        raise HTTPException(status_code=500, detail=f"重置配额失败: {str(e)}")


@router.get("/active/list", response_model=List[ModelConfigOut], summary="获取激活的模型列表（简化）")
async def get_active_models(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取所有激活的模型配置（不分页）
    
    用于前端下拉框等场景。需要用户认证。
    """
    try:
        configs, _ = await ModelConfigService.get_model_configs(
            db, skip=0, limit=1000, active_only=True
        )
        
        return [ModelConfigService.to_output_schema(config) for config in configs]
    except Exception as e:
        logger.error(f"Failed to get active models: {e}")
        raise HTTPException(status_code=500, detail=f"获取激活模型列表失败: {str(e)}")
