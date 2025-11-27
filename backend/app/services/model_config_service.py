"""
模型配置服务
处理模型配置的 CRUD 操作和配额管理
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from ..models.db_models import ModelConfig
from ..models.schemas import ModelConfigCreate, ModelConfigUpdate, ModelConfigOut
from ..core.encryption import encryption_service
import logging

logger = logging.getLogger(__name__)


class ModelConfigService:
    """模型配置服务"""
    
    @staticmethod
    async def create_model_config(db: AsyncSession, data: ModelConfigCreate) -> ModelConfig:
        """
        创建模型配置
        
        Args:
            db: 数据库会话
            data: 创建数据
            
        Returns:
            创建的模型配置
        """
        # 加密 API Key
        encrypted_key = encryption_service.encrypt(data.api_key)
        
        model_config = ModelConfig(
            name=data.name,
            model=data.model,
            api_base=data.api_base,
            api_key_encrypted=encrypted_key,
            description=data.description,
            quota_limit=data.quota_limit,
            quota_reset_cron=data.quota_reset_cron
        )
        
        db.add(model_config)
        await db.commit()
        await db.refresh(model_config)
        
        logger.info(f"Created model config: {model_config.name} (ID: {model_config.id})")
        return model_config
    
    @staticmethod
    async def get_model_config(db: AsyncSession, config_id: int) -> Optional[ModelConfig]:
        """
        获取单个模型配置
        
        Args:
            db: 数据库会话
            config_id: 配置 ID
            
        Returns:
            模型配置或 None
        """
        result = await db.execute(
            select(ModelConfig).where(ModelConfig.id == config_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_model_configs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> tuple[List[ModelConfig], int]:
        """
        获取模型配置列表
        
        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量
            active_only: 是否只返回激活的模型
            
        Returns:
            (模型配置列表, 总数)
        """
        query = select(ModelConfig)
        
        if active_only:
            query = query.where(ModelConfig.is_active == True)
        
        # 获取总数
        count_result = await db.execute(
            select(func.count()).select_from(ModelConfig)
        )
        total = count_result.scalar()
        
        # 获取数据
        query = query.offset(skip).limit(limit).order_by(ModelConfig.created_at.desc())
        result = await db.execute(query)
        configs = result.scalars().all()
        
        return list(configs), total
    
    @staticmethod
    async def update_model_config(
        db: AsyncSession,
        config_id: int,
        data: ModelConfigUpdate
    ) -> Optional[ModelConfig]:
        """
        更新模型配置
        
        Args:
            db: 数据库会话
            config_id: 配置 ID
            data: 更新数据
            
        Returns:
            更新后的模型配置或 None
        """
        config = await ModelConfigService.get_model_config(db, config_id)
        if not config:
            return None
        
        # 更新字段
        update_data = data.dict(exclude_unset=True)
        
        # 如果更新 API Key，需要加密
        if 'api_key' in update_data:
            encrypted_key = encryption_service.encrypt(update_data['api_key'])
            update_data['api_key_encrypted'] = encrypted_key
            del update_data['api_key']
        
        for key, value in update_data.items():
            setattr(config, key, value)
        
        config.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(config)
        
        logger.info(f"Updated model config: {config.name} (ID: {config.id})")
        return config
    
    @staticmethod
    async def delete_model_config(db: AsyncSession, config_id: int) -> bool:
        """
        删除模型配置
        
        Args:
            db: 数据库会话
            config_id: 配置 ID
            
        Returns:
            是否删除成功
        """
        config = await ModelConfigService.get_model_config(db, config_id)
        if not config:
            return False
        
        await db.delete(config)
        await db.commit()
        
        logger.info(f"Deleted model config: {config.name} (ID: {config.id})")
        return True
    
    @staticmethod
    async def reset_quota(
        db: AsyncSession,
        config_id: int,
        new_used: float = 0.0
    ) -> Optional[ModelConfig]:
        """
        重置配额
        
        Args:
            db: 数据库会话
            config_id: 配置 ID
            new_used: 新的使用量
            
        Returns:
            更新后的模型配置或 None
        """
        config = await ModelConfigService.get_model_config(db, config_id)
        if not config:
            return None
        
        config.reset_quota()
        if new_used > 0:
            config.quota_used = new_used
        
        await db.commit()
        await db.refresh(config)
        
        logger.info(f"Reset quota for model config: {config.name} (ID: {config.id})")
        return config
    
    @staticmethod
    def to_output_schema(config: ModelConfig) -> ModelConfigOut:
        """
        转换为输出 Schema
        
        Args:
            config: 模型配置
            
        Returns:
            输出 Schema
        """
        # 解密 API Key 并遮蔽
        try:
            decrypted_key = encryption_service.decrypt(config.api_key_encrypted)
            masked_key = encryption_service.mask_api_key(decrypted_key)
        except Exception as e:
            logger.error(f"Failed to decrypt API key for config {config.id}: {e}")
            masked_key = "****"
        
        return ModelConfigOut(
            id=config.id,
            name=config.name,
            model=config.model,
            model_type=config.model_type,
            api_base=config.api_base,
            api_key_masked=masked_key,
            description=config.description,
            quota_limit=config.quota_limit,
            quota_used=config.quota_used,
            quota_remaining=config.quota_remaining,
            quota_percentage=config.quota_percentage,
            quota_reset_cron=config.quota_reset_cron,
            is_active=config.is_active,
            created_at=config.created_at,
            updated_at=config.updated_at
        )
    
    @staticmethod
    async def get_decrypted_api_key(db: AsyncSession, config_id: int) -> Optional[str]:
        """
        获取解密后的 API Key（仅供内部使用）
        
        Args:
            db: 数据库会话
            config_id: 配置 ID
            
        Returns:
            解密后的 API Key 或 None
        """
        config = await ModelConfigService.get_model_config(db, config_id)
        if not config:
            return None
        
        try:
            return encryption_service.decrypt(config.api_key_encrypted)
        except Exception as e:
            logger.error(f"Failed to decrypt API key for config {config_id}: {e}")
            return None
