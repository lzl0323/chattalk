"""Pydantic 数据模型"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Literal, Dict
from datetime import datetime
import uuid


class Message(BaseModel):
    """聊天消息模型"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "你好，请介绍一下自己",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息内容")
    conversation_id: Optional[str] = Field(None, description="对话 ID，不提供则创建新对话")
    model_config_id: Optional[int] = Field(None, description="模型配置 ID，不提供则使用默认模型")
    stream: bool = Field(True, description="是否使用流式响应")
    model: Optional[str] = Field(None, description="（已废弃）指定模型，请使用 model_config_id")
    
    @validator('message')
    def validate_message(cls, v):
        """验证消息内容"""
        if not v or len(v.strip()) == 0:
            raise ValueError('消息内容不能为空')
        if len(v) > 4000:
            raise ValueError('消息内容过长，最多 4000 字符')
        return v.strip()
    
    class Config:
        protected_namespaces = ()  # 禁用 model_ 命名空间保护
        json_schema_extra = {
            "example": {
                "message": "你好，请介绍一下 FastAPI",
                "conversation_id": None,
                "model_config_id": 1,
                "stream": True
            }
        }


class ChatResponse(BaseModel):
    """聊天响应模型（非流式）"""
    conversation_id: str
    message: str
    model: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "你好！我是 AI 助手...",
                "model": "moonshot-v1-8k",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class StreamChunk(BaseModel):
    """流式响应块模型"""
    type: Literal["content", "done", "error", "suggestions"]
    content: Optional[str] = None
    conversation_id: Optional[str] = None
    error: Optional[str] = None
    suggestions: Optional[List[Dict[str, str]]] = None  # 推荐卡片数据
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "content",
                "content": "你好"
            }
        }


class Conversation(BaseModel):
    """对话模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str):
        """添加消息到对话"""
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_messages_for_api(self, max_messages: int = None) -> List[dict]:
        """
        获取用于 API 调用的消息列表
        
        Args:
            max_messages: 最大消息数量，用于限制上下文长度
            
        Returns:
            消息字典列表
        """
        messages = self.messages
        
        # 限制消息数量（保留最近的消息）
        if max_messages and len(messages) > max_messages:
            messages = messages[-max_messages:]
        
        # 转换为 API 格式
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
            if msg.role != "system"  # system 消息单独处理
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "messages": [
                    {
                        "role": "user",
                        "content": "你好",
                        "timestamp": "2024-01-01T12:00:00"
                    }
                ],
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid request",
                "detail": "消息内容不能为空",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


# ==================== 认证相关模型 ====================

class UserRegister(BaseModel):
    """用户注册请求"""
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="用户密码，6-100字符")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }


class UserLogin(BaseModel):
    """用户登录请求"""
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., description="用户密码")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "is_active": True,
                "created_at": "2024-01-01T12:00:00"
            }
        }


class Token(BaseModel):
    """JWT Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "is_active": True,
                    "created_at": "2024-01-01T12:00:00"
                }
            }
        }


class ApiResponse(BaseModel):
    """标准 API 响应"""
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="消息")
    data: Optional[dict] = Field(default=None, description="数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {}
            }
        }


# ==================== 对话历史相关模型 ====================

class ConversationCreate(BaseModel):
    """创建对话请求"""
    title: Optional[str] = Field(None, max_length=255, description="对话标题")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "关于 Python 的讨论"
            }
        }


class ConversationUpdate(BaseModel):
    """更新对话请求"""
    title: str = Field(..., max_length=255, description="对话标题")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "新的对话标题"
            }
        }


class ConversationListItem(BaseModel):
    """对话列表项"""
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "关于 Python 的讨论",
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T13:00:00",
                "message_count": 5
            }
        }


class ConversationDetail(BaseModel):
    """对话详情"""
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[Message]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "关于 Python 的讨论",
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T13:00:00",
                "messages": []
            }
        }


class MessageCreate(BaseModel):
    """创建消息请求"""
    conversation_id: str = Field(..., description="对话 ID")
    role: Literal["user", "assistant"] = Field(..., description="角色")
    content: str = Field(..., description="消息内容")
    
    @validator('content')
    def validate_content(cls, v):
        """验证消息内容"""
        if not v or len(v.strip()) == 0:
            raise ValueError('消息内容不能为空')
        if len(v) > 10000:
            raise ValueError('消息内容过长，最多 10000 字符')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "你好"
            }
        }


# ==================== 模型配置相关 ====================

class ModelConfigCreate(BaseModel):
    """创建模型配置"""
    name: str = Field(..., description="模型展示名称", min_length=1, max_length=100)
    model: str = Field(..., description="模型标识", min_length=1, max_length=100)
    api_base: str = Field(..., description="API 地址")
    api_key: str = Field(..., description="API Key（明文，会自动加密存储）")
    description: Optional[str] = Field(None, description="模型描述")
    quota_limit: float = Field(1000000.0, description="配额限制（tokens）", ge=0)
    quota_reset_cron: Optional[str] = Field(None, description="配额重置 Cron 表达式")
    
    @validator('api_base')
    def validate_api_base(cls, v):
        """验证 API 地址"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('API 地址必须以 http:// 或 https:// 开头')
        return v.rstrip('/')
    
    class Config:
        protected_namespaces = ()  # 禁用 model_ 命名空间保护
        json_schema_extra = {
            "example": {
                "name": "GPT-4",
                "model": "gpt-4",
                "api_base": "https://api.openai.com/v1",
                "api_key": "sk-1234567890abcdef",
                "description": "OpenAI GPT-4 模型",
                "quota_limit": 1000000,
                "quota_reset_cron": "0 0 1 * *"
            }
        }


class ModelConfigUpdate(BaseModel):
    """更新模型配置"""
    name: Optional[str] = Field(None, description="模型展示名称", min_length=1, max_length=100)
    model: Optional[str] = Field(None, description="模型标识", min_length=1, max_length=100)
    api_base: Optional[str] = Field(None, description="API 地址")
    api_key: Optional[str] = Field(None, description="API Key（明文，会自动加密存储）")
    description: Optional[str] = Field(None, description="模型描述")
    quota_limit: Optional[float] = Field(None, description="配额限制（tokens）", ge=0)
    quota_reset_cron: Optional[str] = Field(None, description="配额重置 Cron 表达式")
    is_active: Optional[bool] = Field(None, description="是否激活")
    
    @validator('api_base')
    def validate_api_base(cls, v):
        """验证 API 地址"""
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('API 地址必须以 http:// 或 https:// 开头')
        return v.rstrip('/') if v else v
    
    class Config:
        protected_namespaces = ()  # 禁用 model_ 命名空间保护


class ModelConfigOut(BaseModel):
    """模型配置输出"""
    id: int
    name: str
    model: str
    model_type: str = Field(default="chat", description="模型类型: chat, ocr, embedding")
    api_base: str
    api_key_masked: str = Field(..., description="遮蔽后的 API Key")
    description: Optional[str]
    quota_limit: float
    quota_used: float
    quota_remaining: float
    quota_percentage: float
    quota_reset_cron: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        protected_namespaces = ()  # 禁用 model_ 命名空间保护
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "GPT-4",
                "model": "gpt-4",
                "api_base": "https://api.openai.com/v1",
                "api_key_masked": "sk-1234****",
                "description": "OpenAI GPT-4 模型",
                "quota_limit": 1000000,
                "quota_used": 50000,
                "quota_remaining": 950000,
                "quota_percentage": 5.0,
                "quota_reset_cron": "0 0 1 * *",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class ModelConfigList(BaseModel):
    """模型配置列表"""
    total: int
    items: List[ModelConfigOut]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 2,
                "items": []
            }
        }


class QuotaResetRequest(BaseModel):
    """配额重置请求"""
    quota_used: float = Field(0.0, description="重置后的使用量", ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "quota_used": 0.0
            }
        }
