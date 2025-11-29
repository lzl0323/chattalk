"""数据库模型"""

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Boolean, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


def generate_uuid():
    """生成 UUID"""
    return str(uuid.uuid4())


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # 关系
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Conversation(Base):
    """对话表"""
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), default="新对话", nullable=True)  # 对话标题
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, title={self.title})>"


class Message(Base):
    """消息表"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # OCR 相关字段
    message_type = Column(String(20), default="text", nullable=False)  # text, ocr, image
    file_url = Column(String(500), nullable=True)  # 文件存储路径
    file_name = Column(String(255), nullable=True)  # 原始文件名
    ocr_mode = Column(String(50), nullable=True)  # markdown, general, free_ocr, chart, describe, locate
    
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, type={self.message_type})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "message_type": self.message_type,
            "file_url": self.file_url,
            "file_name": self.file_name,
            "ocr_mode": self.ocr_mode,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ModelConfig(Base):
    """AI 模型配置表"""
    __tablename__ = "model_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # 展示名称，例如 "GPT-4"
    model = Column(String(100), nullable=False)  # 模型标识，例如 "gpt-4", "deepseek-chat"
    model_type = Column(String(20), default="chat", nullable=False)  # chat, ocr, embedding
    api_base = Column(String(255), nullable=False)  # API 地址
    api_key_encrypted = Column(Text, nullable=False)  # 加密后的 API Key
    description = Column(Text, nullable=True)  # 模型描述
    
    # 配额管理
    quota_limit = Column(Float, default=1000000.0, nullable=False)  # 总配额（tokens）
    quota_used = Column(Float, default=0.0, nullable=False)  # 已使用配额
    quota_reset_cron = Column(String(50), nullable=True)  # Cron 表达式，用于自动重置
    is_active = Column(Boolean, default=True, nullable=False)  # 是否激活
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    def __repr__(self):
        return f"<ModelConfig(id={self.id}, name={self.name}, model={self.model}, is_active={self.is_active})>"
    
    @property
    def quota_remaining(self) -> float:
        """剩余配额"""
        return max(0, self.quota_limit - self.quota_used)
    
    @property
    def quota_percentage(self) -> float:
        """配额使用百分比"""
        if self.quota_limit == 0:
            return 100.0
        return (self.quota_used / self.quota_limit) * 100
    
    def is_quota_exceeded(self) -> bool:
        """检查配额是否用尽"""
        return self.quota_used >= self.quota_limit
    
    def increment_quota(self, tokens: float) -> None:
        """
        增加配额使用量
        
        Args:
            tokens: 使用的 token 数量
        """
        self.quota_used += tokens
        
        # 如果配额用尽，自动禁用
        if self.is_quota_exceeded() and self.is_active:
            self.is_active = False
    
    def reset_quota(self) -> None:
        """重置配额"""
        self.quota_used = 0.0
        self.is_active = True


class SuggestionRecord(Base):
    """推荐问题记录表"""
    __tablename__ = "suggestion_records"
    __table_args__ = (
        # 添加唯一约束：同一用户不能有相同标题的推荐
        UniqueConstraint('user_id', 'title', name='uq_user_title'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    suggestion_type = Column(String(20), nullable=False)  # trending, research, personalized, general
    title = Column(String(100), nullable=False)  # 推荐问题标题
    icon = Column(String(20), default="bolt")  # 图标
    is_clicked = Column(Boolean, default=False)  # 是否被点击
    clicked_at = Column(DateTime, nullable=True)  # 点击时间
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    
    # 关系
    user = relationship("User", backref="suggestion_records")
    
    def __repr__(self):
        return f"<SuggestionRecord(id={self.id}, user_id={self.user_id}, title={self.title})>"


class KnowledgeBase(Base):
    """知识库表"""
    __tablename__ = "knowledge_bases"
    
    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    document_count = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # 关系
    user = relationship("User", backref="knowledge_bases")
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, name={self.name}, user_id={self.user_id})>"


class Document(Base):
    """文档表"""
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True)  # UUID
    knowledge_base_id = Column(String(36), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)  # 原始文件路径
    file_type = Column(String(50), nullable=True)  # pdf, txt, docx, md
    file_size = Column(Integer, nullable=True)  # 字节
    
    content = Column(Text, nullable=False)  # 文档内容
    chunk_count = Column(Integer, default=0)  # chunk 数量
    
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    user = relationship("User", backref="documents")
    
    def __repr__(self):
        return f"<Document(id={self.id}, file_name={self.file_name}, kb_id={self.knowledge_base_id})>"
