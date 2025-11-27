"""对话历史管理 API"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db
from ..core.auth import get_current_user
from ..models.db_models import User, Conversation, Message as DBMessage
from ..models.schemas import (
    ConversationCreate,
    ConversationUpdate,
    ConversationListItem,
    ConversationDetail,
    MessageCreate,
    Message,
    ApiResponse
)

router = APIRouter(prefix="/api/conversations", tags=["对话历史"])


@router.post("/", response_model=ConversationDetail, summary="创建新对话")
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建新对话
    
    - **title**: 对话标题（可选）
    
    返回：新创建的对话详情
    """
    # 创建新对话
    new_conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title
    )
    
    db.add(new_conversation)
    await db.commit()
    await db.refresh(new_conversation)
    
    return ConversationDetail(
        id=new_conversation.id,
        title=new_conversation.title,
        created_at=new_conversation.created_at,
        updated_at=new_conversation.updated_at,
        messages=[]
    )


@router.get("/", response_model=List[ConversationListItem], summary="获取对话列表")
async def get_conversations(
    search: Optional[str] = Query(None, description="搜索关键词（标题）"),
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的对话列表
    
    - **search**: 搜索关键词（可选）
    - **limit**: 返回数量（默认50）
    - **offset**: 偏移量（默认0）
    
    返回：按更新时间倒序排列的对话列表
    """
    # 构建查询
    query = select(Conversation).where(Conversation.user_id == current_user.id)
    
    # 添加搜索条件
    if search:
        query = query.where(Conversation.title.like(f"%{search}%"))
    
    # 排序和分页
    query = query.order_by(desc(Conversation.updated_at)).limit(limit).offset(offset)
    
    # 执行查询
    result = await db.execute(query)
    conversations = result.scalars().all()
    
    # 构建响应
    conversation_list = []
    for conv in conversations:
        # 获取消息数量
        msg_count_query = select(func.count(DBMessage.id)).where(
            DBMessage.conversation_id == conv.id
        )
        msg_count_result = await db.execute(msg_count_query)
        msg_count = msg_count_result.scalar()
        
        conversation_list.append(
            ConversationListItem(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=msg_count
            )
        )
    
    return conversation_list


@router.get("/{conversation_id}", response_model=ConversationDetail, summary="获取对话详情")
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定对话的详细信息和所有消息
    
    - **conversation_id**: 对话ID
    
    返回：对话详情和完整消息历史
    """
    # 查找对话
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 获取消息
    msg_result = await db.execute(
        select(DBMessage)
        .where(DBMessage.conversation_id == conversation_id)
        .order_by(DBMessage.timestamp)
    )
    messages = msg_result.scalars().all()
    
    # 转换消息格式
    message_list = [
        Message(
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp
        )
        for msg in messages
    ]
    
    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=message_list
    )


@router.put("/{conversation_id}", response_model=ConversationDetail, summary="更新对话")
async def update_conversation(
    conversation_id: str,
    conversation_data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新对话标题
    
    - **conversation_id**: 对话ID
    - **title**: 新的对话标题
    """
    # 查找对话
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 更新标题
    conversation.title = conversation_data.title
    conversation.updated_at = datetime.now()
    
    await db.commit()
    await db.refresh(conversation)
    
    # 获取消息
    msg_result = await db.execute(
        select(DBMessage)
        .where(DBMessage.conversation_id == conversation_id)
        .order_by(DBMessage.timestamp)
    )
    messages = msg_result.scalars().all()
    
    message_list = [
        Message(
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp
        )
        for msg in messages
    ]
    
    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=message_list
    )


@router.delete("/{conversation_id}", response_model=ApiResponse, summary="删除对话")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除指定对话及其所有消息
    
    - **conversation_id**: 对话ID
    """
    # 查找对话
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 删除对话（级联删除消息）
    await db.delete(conversation)
    await db.commit()
    
    return ApiResponse(
        code=200,
        message="对话已删除",
        data={"conversation_id": conversation_id}
    )


@router.post("/messages", response_model=Message, summary="添加消息")
async def create_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    向指定对话添加消息
    
    - **conversation_id**: 对话ID
    - **role**: 角色（user 或 assistant）
    - **content**: 消息内容
    
    注意：此接口主要用于保存消息记录，实时聊天请使用 /api/chat 接口
    """
    # 验证对话是否存在且属于当前用户
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == message_data.conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    # 创建消息
    new_message = DBMessage(
        conversation_id=message_data.conversation_id,
        role=message_data.role,
        content=message_data.content
    )
    
    db.add(new_message)
    
    # 更新对话的更新时间
    conversation.updated_at = datetime.now()
    
    await db.commit()
    await db.refresh(new_message)
    
    return Message(
        role=new_message.role,
        content=new_message.content,
        timestamp=new_message.timestamp
    )
