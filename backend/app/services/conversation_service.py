"""对话服务 - 数据库操作"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timedelta

from ..models.db_models import Conversation, Message


class ConversationService:
    """对话服务类"""
    
    @staticmethod
    async def create_conversation(db: AsyncSession, user_id: int, title: str = None) -> Conversation:
        """创建新对话"""
        conversation = Conversation(user_id=user_id, title=title)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation
    
    @staticmethod
    async def get_conversation(
        db: AsyncSession,
        conversation_id: str,
        include_messages: bool = True
    ) -> Optional[Conversation]:
        """获取对话"""
        query = select(Conversation).where(Conversation.id == conversation_id)
        
        if include_messages:
            query = query.options(selectinload(Conversation.messages))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def add_message(
        db: AsyncSession,
        conversation_id: str,
        role: str,
        content: str
    ) -> Message:
        """添加消息到对话"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        db.add(message)
        
        # 更新对话的 updated_at
        conversation = await ConversationService.get_conversation(
            db, conversation_id, include_messages=False
        )
        if conversation:
            conversation.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(message)
        return message
    
    @staticmethod
    async def get_messages(
        db: AsyncSession,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """获取对话的所有消息"""
        query = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
        
        if limit:
            query = query.limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_conversation_title(db: AsyncSession, conversation_id: str, title: str) -> bool:
        """更新对话标题"""
        conversation = await ConversationService.get_conversation(db, conversation_id, include_messages=False)
        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.now()
            await db.commit()
            return True
        return False
    
    @staticmethod
    async def get_message_count(db: AsyncSession, conversation_id: str) -> int:
        """获取对话的消息数量"""
        query = select(func.count()).select_from(Message).where(Message.conversation_id == conversation_id)
        result = await db.execute(query)
        return result.scalar() or 0
    
    @staticmethod
    async def delete_conversation(db: AsyncSession, conversation_id: str) -> bool:
        """删除对话"""
        result = await db.execute(
            delete(Conversation).where(Conversation.id == conversation_id)
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def clean_old_conversations(db: AsyncSession, hours: int = 24) -> int:
        """清理指定时间之前的对话"""
        threshold = datetime.now() - timedelta(hours=hours)
        result = await db.execute(
            delete(Conversation).where(Conversation.updated_at < threshold)
        )
        await db.commit()
        return result.rowcount
    
    @staticmethod
    async def get_conversation_count(db: AsyncSession) -> int:
        """获取对话总数"""
        from sqlalchemy import func
        result = await db.execute(select(func.count(Conversation.id)))
        return result.scalar_one()
