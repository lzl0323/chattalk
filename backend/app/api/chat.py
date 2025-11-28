"""聊天 API 端点 - 使用 SQLite 数据库"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json
import logging
from datetime import datetime

from ..models.schemas import ChatRequest, ChatResponse, StreamChunk
from ..models.db_models import User, ModelConfig
from ..services.kimi import kimi_service
from ..services.conversation_service import ConversationService
from ..services.model_config_service import ModelConfigService
from ..services.openai_service import (
    openai_client_service,
    ModelQuotaExceeded,
    ModelNotActive
)
from ..core.config import settings
from ..core.prompts import build_messages_with_system
from ..core.database import get_db
from ..core.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


async def get_or_create_conversation(db: AsyncSession, user_id: int, conversation_id: str = None, title: str = None):
    """获取或创建对话"""
    if conversation_id:
        conversation = await ConversationService.get_conversation(db, conversation_id)
        if conversation:
            return conversation
    
    # 创建新对话
    conversation = await ConversationService.create_conversation(db, user_id=user_id, title=title)
    logger.info(f"Created new conversation: {conversation.id} for user: {user_id}")
    return conversation


async def get_model_config(db: AsyncSession, model_config_id: Optional[int] = None) -> ModelConfig:
    """
    获取模型配置
    
    Args:
        db: 数据库会话
        model_config_id: 模型配置 ID
        
    Returns:
        模型配置
        
    Raises:
        HTTPException: 模型不存在或未激活
    """
    if model_config_id:
        config = await ModelConfigService.get_model_config(db, model_config_id)
        if not config:
            raise HTTPException(status_code=404, detail="模型配置不存在")
    else:
        # 获取默认模型（第一个激活的模型）
        configs, _ = await ModelConfigService.get_model_configs(db, limit=1, active_only=True)
        if not configs:
            raise HTTPException(status_code=503, detail="没有可用的模型配置，请联系管理员")
        config = configs[0]
    
    # 检查配额
    try:
        await openai_client_service.check_quota(config)
    except ModelNotActive as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ModelQuotaExceeded as e:
        raise HTTPException(status_code=429, detail=str(e))
    
    return config


async def generate_stream(
    db: AsyncSession,
    config: ModelConfig,
    conversation_id: str,
    user_message: str,
    current_user,
    save_user_message: bool = True
):
    """生成流式响应（使用 OpenAI 客户端）"""
    try:
        # 添加用户消息到数据库（可选）
        if save_user_message:
            await ConversationService.add_message(db, conversation_id, "user", user_message)
        
        # 获取对话消息（限制最近 N 条）
        messages_list = await ConversationService.get_messages(
            db, conversation_id, limit=settings.max_context_messages
        )
        
        # 转换为 API 格式
        user_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages_list
            if msg.role != "system"
        ]
        
        # 如果未保存用户消息，手动添加到上下文中
        if not save_user_message:
            user_messages.append({"role": "user", "content": user_message})
        
        # 构建消息列表（包含 system prompt）
        messages = build_messages_with_system(user_messages)
        
        logger.info(
            f"Sending to OpenAI API, model: {config.name} ({config.model}), "
            f"conversation: {conversation_id}, messages: {len(messages)}"
        )
        
        # 收集完整的助手回复
        assistant_message = ""
        
        # 调用 OpenAI API（流式）
        response = await openai_client_service.chat_completion(
            config=config,
            messages=messages,
            stream=True
        )
        
        # 处理流式响应
        async for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:
                    assistant_message += delta.content
                    
                    # 发送内容块
                    chunk_data = StreamChunk(type="content", content=delta.content)
                    yield f"data: {chunk_data.model_dump_json()}\n\n"
        
        # 保存助手回复到数据库
        await ConversationService.add_message(db, conversation_id, "assistant", assistant_message)
        
        # 估算 token 使用（流式响应没有 usage 信息，使用粗略估算）
        estimated_tokens = len(assistant_message) / 4 + len(user_message) / 4
        await openai_client_service.update_quota_usage(db, config, estimated_tokens)
        
        # 检查是否需要插入推荐卡片（每3轮对话插入一次）
        message_count = await ConversationService.get_message_count(db, conversation_id)
        should_show_suggestions = message_count > 0 and message_count % 6 == 0  # 每6条消息（3轮对话）
        
        if should_show_suggestions:
            # 生成推荐卡片
            from ..services.suggestion_service import SuggestionService
            suggestions = await SuggestionService.get_fallback_suggestions(
                db=db,
                user_id=current_user.id,
                count=3  # 对话中只显示3个推荐
            )
            
            # 发送推荐卡片
            suggestions_data = StreamChunk(
                type="suggestions",
                suggestions=suggestions
            )
            yield f"data: {suggestions_data.model_dump_json()}\n\n"
        
        # 发送完成标记
        done_data = StreamChunk(
            type="done",
            conversation_id=conversation_id
        )
        yield f"data: {done_data.model_dump_json()}\n\n"
        
        logger.info(
            f"Stream completed for conversation: {conversation_id}, "
            f"tokens: ~{estimated_tokens:.0f}"
        )
        
    except ModelQuotaExceeded as e:
        logger.warning(f"Quota exceeded: {e}")
        error_data = StreamChunk(type="error", error=str(e))
        yield f"data: {error_data.model_dump_json()}\n\n"
        
    except Exception as e:
        logger.error(f"Error in generate_stream: {e}", exc_info=True)
        error_data = StreamChunk(type="error", error=str(e))
        yield f"data: {error_data.model_dump_json()}\n\n"


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    聊天接口（需要认证，支持动态模型选择）
    
    - **message**: 用户消息内容
    - **conversation_id**: 可选，对话 ID，不提供则创建新对话
    - **model_config_id**: 可选，模型配置 ID，不提供则使用默认模型
    - **stream**: 是否使用流式响应（默认 True）
    
    需要提供有效的 Bearer Token。
    自动进行配额检查，配额用尽时返回 429 错误。
    """
    try:
        # 获取模型配置
        config = await get_model_config(db, request.model_config_id)
        
        # 获取或创建对话
        conversation = await get_or_create_conversation(db, current_user.id, request.conversation_id)
        conversation_id = conversation.id
        
        # 如果是新对话且没有标题，使用第一条消息作为标题
        if not conversation.title or conversation.title == "新对话":
            # 截取消息前20个字符作为标题
            title = request.message[:20] + "..." if len(request.message) > 20 else request.message
            await ConversationService.update_conversation_title(db, conversation_id, title)
        
        # 流式响应
        if request.stream:
            return StreamingResponse(
                generate_stream(db, config, conversation_id, request.message, current_user, request.save_user_message),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
                }
            )
        
        # 非流式响应
        else:
            # 添加用户消息
            await ConversationService.add_message(db, conversation_id, "user", request.message)
            
            # 获取对话消息
            messages_list = await ConversationService.get_messages(
                db, conversation_id, limit=settings.max_context_messages
            )
            
            # 转换为 API 格式
            user_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages_list
                if msg.role != "system"
            ]
            
            # 构建消息列表
            messages = build_messages_with_system(user_messages)
            
            # 调用 OpenAI API（非流式）
            response = await openai_client_service.chat_completion(
                config=config,
                messages=messages,
                stream=False
            )
            
            response_content = response.choices[0].message.content
            
            # 保存助手回复
            await ConversationService.add_message(db, conversation_id, "assistant", response_content)
            
            # 更新配额
            tokens = openai_client_service.calculate_tokens_from_response(response)
            await openai_client_service.update_quota_usage(db, config, tokens)
            
            logger.info(
                f"Chat completed for conversation: {conversation_id}, "
                f"model: {config.name}, tokens: {tokens:.0f}"
            )
            
            # 返回响应
            return ChatResponse(
                conversation_id=conversation_id,
                message=response_content,
                model=config.model
            )
            
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """获取对话历史"""
    conversation = await ConversationService.get_conversation(db, conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    return {
        "conversation_id": conversation.id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat(),
                "message_type": msg.message_type,
                "file_url": msg.file_url,
                "file_name": msg.file_name,
                "ocr_mode": msg.ocr_mode
            }
            for msg in conversation.messages
        ],
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat()
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """删除对话"""
    deleted = await ConversationService.delete_conversation(db, conversation_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    logger.info(f"Deleted conversation: {conversation_id}")
    return {"message": "对话已删除"}


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """健康检查"""
    conversation_count = await ConversationService.get_conversation_count(db)
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_conversations": conversation_count,
        "database": "sqlite"
    }
