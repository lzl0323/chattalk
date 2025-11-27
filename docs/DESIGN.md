# AI 对话系统 - 详细设计文档

## 1. 系统架构

### 1.1 整体架构

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   浏览器     │ ──────> │    Nginx    │ ──────> │   FastAPI   │ ──────> │  Kimi API   │
│  (Vue3 SPA) │ <────── │  反向代理    │ <────── │   后端服务   │ <────── │  (OpenAI)   │
└─────────────┘         └─────────────┘         └─────────────┘         └─────────────┘
     │                         │                         │
     │                         │                         │
  用户交互              静态文件服务            流式转发 + 上下文管理
  SSE 接收              API 路由转发            System Prompt 注入
```

### 1.2 数据流

**请求流程**:
1. 用户在 Vue3 界面输入消息
2. 前端通过 Axios 发送 POST 请求到 `/api/chat`
3. Nginx 将请求转发到 FastAPI (localhost:8000)
4. FastAPI 处理请求：
   - 验证输入
   - 加载/创建对话上下文
   - 注入 System Prompt
   - 构建完整的消息历史
5. FastAPI 调用 Kimi API（OpenAI-compatible）
6. Kimi API 返回流式响应
7. FastAPI 转发流式数据（SSE 格式）
8. Nginx 透传流式响应（禁用缓冲）
9. 前端接收并实时渲染

## 2. 前端架构设计

### 2.1 技术选型理由

- **Vue3**: Composition API 提供更好的逻辑复用和类型推导
- **Vite**: 快速的开发服务器和优化的生产构建
- **TailwindCSS**: 实用优先的 CSS 框架，快速构建现代 UI
- **Axios**: 成熟的 HTTP 客户端，易于配置和拦截

### 2.2 组件设计

#### ChatContainer.vue (聊天容器)
**职责**:
- 管理对话状态（消息列表、加载状态）
- 处理用户发送消息
- 协调子组件交互

**状态**:
```javascript
{
  messages: [],           // 消息列表
  isLoading: false,       // 加载状态
  conversationId: null,   // 对话 ID
  currentMessage: ''      // 当前正在接收的流式消息
}
```

#### ChatMessage.vue (消息气泡)
**职责**:
- 渲染单条消息
- 区分用户/AI 消息样式
- 支持 Markdown 渲染（可选）

**Props**:
```javascript
{
  role: 'user' | 'assistant',
  content: String,
  timestamp: Date
}
```

#### ChatInput.vue (输入框)
**职责**:
- 用户输入
- 发送按钮
- 快捷键支持（Enter 发送）
- 输入验证

**Events**:
```javascript
emit('send', message)
```

### 2.3 流式响应处理

使用 `EventSource` API 或 `fetch` 流式处理：

```javascript
// 方案 1: EventSource (推荐)
const eventSource = new EventSource('/api/chat?message=xxx')
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  // 处理流式数据
}

// 方案 2: Fetch Stream
const response = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({ message })
})
const reader = response.body.getReader()
const decoder = new TextDecoder()

while (true) {
  const { done, value } = await reader.read()
  if (done) break
  const text = decoder.decode(value)
  // 处理 SSE 格式的文本
}
```

### 2.4 样式设计

**设计原则**:
- 清晰的视觉层次
- 流畅的动画过渡
- 响应式布局
- 无障碍支持

**配色方案**:
- 背景: `#F9FAFB` (灰白)
- 用户消息: `#3B82F6` (蓝色)
- AI 消息: `#FFFFFF` (白色 + 边框)
- 强调色: `#10B981` (绿色)

## 3. 后端架构设计

### 3.1 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── api/
│   │   └── chat.py          # 聊天端点
│   ├── core/
│   │   ├── config.py        # 配置管理
│   │   └── prompts.py       # System Prompt
│   ├── services/
│   │   └── kimi.py          # Kimi API 客户端
│   └── models/
│       └── schemas.py       # Pydantic 模型
```

### 3.2 核心模块

#### 3.2.1 配置管理 (config.py)

使用 Pydantic BaseSettings 管理配置：

```python
class Settings(BaseSettings):
    kimi_api_key: str
    kimi_api_base: str = "https://api.moonshot.cn/v1"
    kimi_model: str = "moonshot-v1-8k"
    max_context_messages: int = 10
    
    class Config:
        env_file = ".env"
```

#### 3.2.2 Kimi 服务 (kimi.py)

封装 Kimi API 调用：

```python
class KimiService:
    async def chat_stream(
        self, 
        messages: List[Dict], 
        model: str
    ) -> AsyncGenerator[str, None]:
        # 流式调用 Kimi API
        # 使用 httpx.AsyncClient
        # 逐块 yield 响应
```

#### 3.2.3 聊天端点 (chat.py)

```python
@router.post("/chat")
async def chat(request: ChatRequest):
    # 1. 验证输入
    # 2. 加载对话上下文
    # 3. 注入 System Prompt
    # 4. 调用 Kimi 服务
    # 5. 返回 StreamingResponse
```

### 3.3 上下文管理策略

**内存存储方案** (适合演示):
```python
# 全局字典存储对话
conversations = {}

# 结构
{
  "conversation_id": {
    "messages": [...],
    "created_at": timestamp,
    "updated_at": timestamp
  }
}
```

**清理策略**:
- 限制每个对话的消息数量（如 10 条）
- 定期清理过期对话（如 1 小时未活动）

**生产环境建议**:
- 使用 Redis 存储会话
- 使用数据库持久化历史
- 实现用户认证和隔离

### 3.4 流式响应实现

```python
async def generate_stream():
    async for chunk in kimi_service.chat_stream(messages):
        # SSE 格式
        yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
    yield f"data: {json.dumps({'type': 'done'})}\n\n"

return StreamingResponse(
    generate_stream(),
    media_type="text/event-stream"
)
```

### 3.5 异常处理

**分层处理**:
1. **输入验证**: Pydantic 自动验证
2. **业务异常**: 自定义异常类
3. **外部 API 异常**: 捕获并包装
4. **流式异常**: 通过 SSE 事件传递错误

```python
try:
    async for chunk in stream:
        yield chunk
except Exception as e:
    logger.error(f"Stream error: {e}")
    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
```

## 4. System Prompt 设计

### 4.1 设计目标

- 定义 AI 助手的角色和行为
- 确保回答的专业性和一致性
- 规范输出格式
- 设置安全边界

### 4.2 Prompt 结构

```markdown
# 角色定义
你是一个专业、友好的 AI 助手...

# 核心能力
- 回答各类问题
- 提供建议和指导
- 进行分析和总结

# 回答风格
- 清晰简洁
- 结构化组织
- 使用 Markdown 格式

# 格式规范
- 使用 ## 标题组织内容
- 使用列表呈现要点
- 使用代码块展示代码
- 使用表格展示对比

# 安全规范
- 拒绝不当请求
- 保护隐私信息
- 承认知识边界

# 特殊指令
- 对于代码问题，提供可运行的示例
- 对于概念解释，使用类比和例子
```

### 4.3 动态 Prompt

支持根据上下文动态调整：

```python
def build_system_prompt(context: Dict) -> str:
    base_prompt = load_base_prompt()
    
    # 根据用户偏好调整
    if context.get('technical_level') == 'beginner':
        base_prompt += "\n请用简单易懂的语言解释。"
    
    return base_prompt
```

## 5. Nginx 配置设计

### 5.1 核心配置

```nginx
# 静态文件服务
location / {
    root /path/to/frontend/dist;
    try_files $uri $uri/ /index.html;
}

# API 反向代理
location /api/ {
    proxy_pass http://localhost:8000/api/;
    
    # 流式支持
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 300s;
    
    # SSE 必需的头
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    chunked_transfer_encoding off;
}
```

### 5.2 优化配置

- **Gzip 压缩**: 减小传输大小
- **缓存策略**: 静态资源长期缓存，API 不缓存
- **SSL/TLS**: HTTPS 配置
- **安全头**: CSP, X-Frame-Options 等

## 6. 数据模型

### 6.1 后端模型 (Pydantic)

```python
class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    stream: bool = True
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        if len(v) > 4000:
            raise ValueError('Message too long')
        return v.strip()

class Conversation(BaseModel):
    id: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
```

### 6.2 前端模型 (TypeScript/JSDoc)

```javascript
/**
 * @typedef {Object} Message
 * @property {string} role - 'user' | 'assistant'
 * @property {string} content
 * @property {Date} timestamp
 */

/**
 * @typedef {Object} ChatState
 * @property {Message[]} messages
 * @property {boolean} isLoading
 * @property {string|null} conversationId
 * @property {string} currentStreamMessage
 */
```

## 7. 性能优化

### 7.1 前端优化

- **虚拟滚动**: 大量消息时使用虚拟列表
- **防抖**: 输入框输入时的防抖处理
- **懒加载**: 按需加载历史消息
- **代码分割**: 路由级别的代码分割

### 7.2 后端优化

- **连接池**: httpx AsyncClient 复用
- **并发限制**: 限制同时处理的请求数
- **缓存**: 缓存常用的 System Prompt
- **监控**: 添加性能监控和日志

### 7.3 网络优化

- **HTTP/2**: 多路复用
- **压缩**: Gzip/Brotli
- **CDN**: 静态资源 CDN 加速
- **Keep-Alive**: 复用 TCP 连接

## 8. 安全考虑

### 8.1 API 安全

- **速率限制**: 防止滥用
- **输入验证**: 严格验证所有输入
- **输出转义**: 防止 XSS
- **API 密钥保护**: 环境变量 + 服务端存储

### 8.2 传输安全

- **HTTPS**: 加密传输
- **CORS**: 限制允许的源
- **CSP**: 内容安全策略
- **HSTS**: 强制 HTTPS

### 8.3 数据安全

- **敏感信息过滤**: 不记录敏感数据
- **会话隔离**: 用户间数据隔离
- **定期清理**: 清理过期数据

## 9. 监控和日志

### 9.1 日志策略

```python
# 结构化日志
logger.info("Chat request", extra={
    "conversation_id": conv_id,
    "message_length": len(message),
    "user_ip": request.client.host
})

# 错误日志
logger.error("Kimi API error", extra={
    "error": str(e),
    "request_id": request_id
}, exc_info=True)
```

### 9.2 监控指标

- **请求量**: QPS、成功率
- **延迟**: P50、P95、P99
- **错误率**: 按类型分类
- **资源使用**: CPU、内存、带宽

## 10. 测试策略

### 10.1 单元测试

- 后端: pytest
- 前端: Vitest

### 10.2 集成测试

- API 端到端测试
- 流式响应测试

### 10.3 E2E 测试

- Playwright/Cypress
- 模拟真实用户交互

## 11. 扩展性设计

### 11.1 多模型支持

```python
class ModelFactory:
    @staticmethod
    def create(model_type: str):
        if model_type == 'kimi':
            return KimiService()
        elif model_type == 'gpt':
            return GPTService()
        # ...
```

### 11.2 插件系统

- 消息预处理插件
- 消息后处理插件
- 自定义工具/函数调用

### 11.3 多租户

- 用户认证
- 配额管理
- 数据隔离

## 总结

本设计文档提供了一个完整、可扩展的 AI 对话系统架构。核心特点：

- **模块化**: 清晰的职责分离
- **可扩展**: 易于添加新功能
- **高性能**: 流式响应 + 优化配置
- **安全性**: 多层安全防护
- **可维护**: 完善的日志和监控

下一步可以根据实际需求进行调整和扩展。
