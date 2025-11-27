"""
OpenAI 客户端服务
根据模型配置动态创建和管理 OpenAI 客户端
"""
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, AsyncIterator
import logging

from ..models.db_models import ModelConfig
from ..core.encryption import encryption_service

logger = logging.getLogger(__name__)


class ModelQuotaExceeded(Exception):
    """模型配额已用尽异常"""
    pass


class ModelNotActive(Exception):
    """模型未激活异常"""
    pass


class OpenAIClientService:
    """OpenAI 客户端服务"""
    
    @staticmethod
    def create_client(api_key: str, api_base: str) -> AsyncOpenAI:
        """
        创建 OpenAI 客户端
        
        Args:
            api_key: API Key
            api_base: API 地址
            
        Returns:
            AsyncOpenAI 客户端
        """
        return AsyncOpenAI(
            api_key=api_key,
            base_url=api_base,
            timeout=60.0
        )
    
    @staticmethod
    async def check_quota(config: ModelConfig) -> None:
        """
        检查配额
        
        Args:
            config: 模型配置
            
        Raises:
            ModelNotActive: 模型未激活
            ModelQuotaExceeded: 配额已用尽
        """
        if not config.is_active:
            raise ModelNotActive(f"模型 '{config.name}' 已被禁用")
        
        if config.is_quota_exceeded():
            raise ModelQuotaExceeded(
                f"模型 '{config.name}' 配额已用尽 "
                f"({config.quota_used:.0f}/{config.quota_limit:.0f} tokens)"
            )
    
    @staticmethod
    async def chat_completion(
        config: ModelConfig,
        messages: list,
        stream: bool = True,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """
        调用聊天完成 API
        
        Args:
            config: 模型配置
            messages: 消息列表
            stream: 是否流式响应
            temperature: 温度参数
            max_tokens: 最大 tokens
            
        Returns:
            响应对象
        """
        # 解密 API Key
        api_key = encryption_service.decrypt(config.api_key_encrypted)
        
        # 创建客户端
        client = OpenAIClientService.create_client(api_key, config.api_base)
        
        # 调用 API
        try:
            response = await client.chat.completions.create(
                model=config.model,
                messages=messages,
                stream=stream,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    @staticmethod
    def calculate_tokens_from_response(response) -> float:
        """
        从响应中计算 token 使用量
        
        Args:
            response: OpenAI 响应对象
            
        Returns:
            使用的 token 数量
        """
        # 尝试获取 usage 信息
        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            
            # 优先使用 total_tokens
            if hasattr(usage, 'total_tokens') and usage.total_tokens:
                return float(usage.total_tokens)
            
            # 否则计算 prompt_tokens + completion_tokens
            prompt_tokens = getattr(usage, 'prompt_tokens', 0) or 0
            completion_tokens = getattr(usage, 'completion_tokens', 0) or 0
            total = prompt_tokens + completion_tokens
            
            if total > 0:
                return float(total)
        
        # 如果没有 usage 信息，默认计数为 1 次调用
        logger.warning("No token usage information in response, counting as 1 call")
        return 1.0
    
    @staticmethod
    async def update_quota_usage(
        db: AsyncSession,
        config: ModelConfig,
        tokens: float
    ) -> None:
        """
        更新配额使用量
        
        Args:
            db: 数据库会话
            config: 模型配置
            tokens: 使用的 token 数量
        """
        config.increment_quota(tokens)
        await db.commit()
        await db.refresh(config)
        
        logger.info(
            f"Updated quota for model '{config.name}': "
            f"+{tokens:.0f} tokens, "
            f"total: {config.quota_used:.0f}/{config.quota_limit:.0f} "
            f"({config.quota_percentage:.1f}%)"
        )
        
        if not config.is_active:
            logger.warning(f"Model '{config.name}' has been deactivated due to quota exhaustion")


# 全局服务实例
openai_client_service = OpenAIClientService()
