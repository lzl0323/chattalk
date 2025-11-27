# API 文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **认证**: 目前无需认证（生产环境应添加）

---

## 端点列表

### 1. 根路径

**GET** `/`

获取 API 基本信息。

**响应示例**:
```json
{
  "name": "AI 对话系统 API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "health": "/api/health"
}
```

---

### 2. 健康检查

**GET** `/api/health`

检查服务健康状态。

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "active_conversations": 5
}
```

---

### 3. 聊天接口

**POST** `/api/chat`

发送消息并接收回复（支持流式和非流式）。

#### 请求体

```json
{
  "message": "你好，请介绍一下自己",
  "conversation_id": "uuid-string-optional",
  "stream": true,
  "model": "moonshot-v1-8k"
}
```

#### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| message | string | ✅ | 用户消息内容（1-4000 字符） |
| conversation_id | string | ❌ | 对话 ID，不提供则创建新对话 |
| stream | boolean | ❌ | 是否使用流式响应（默认 true） |
| model | string | ❌ | 指定模型（默认使用配置的模型） |

#### 流式响应 (stream: true)

**Content-Type**: `text/event-stream`

**SSE 事件格式**:

```
data: {"type": "content", "content": "你"}\n\n
data: {"type": "content", "content": "好"}\n\n
data: {"type": "content", "content": "！"}\n\n
data: {"type": "done", "conversation_id": "uuid-string"}\n\n
```

**事件类型**:

1. **content**: AI 回复内容块
   ```json
   {
     "type": "content",
     "content": "文本内容"
   }
   ```

2. **done**: 流式响应完成
   ```json
   {
     "type": "done",
     "conversation_id": "uuid-string"
   }
   ```

3. **error**: 发生错误
   ```json
   {
     "type": "error",
     "error": "错误信息"
   }
   ```

#### 非流式响应 (stream: false)

**Content-Type**: `application/json`

**响应示例**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "你好！我是一个 AI 助手...",
  "model": "moonshot-v1-8k",
  "timestamp": "2024-01-01T12:00:00"
}
```

#### 错误响应

**400 Bad Request**: 参数错误
```json
{
  "detail": "消息内容不能为空"
}
```

**500 Internal Server Error**: 服务器错误
```json
{
  "detail": "服务器错误: 具体错误信息"
}
```

---

### 4. 获取对话历史

**GET** `/api/conversations/{conversation_id}`

获取指定对话的完整历史。

**路径参数**:
- `conversation_id`: 对话 ID (UUID)

**响应示例**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "role": "user",
      "content": "你好",
      "timestamp": "2024-01-01T12:00:00"
    },
    {
      "role": "assistant",
      "content": "你好！有什么我可以帮助你的吗？",
      "timestamp": "2024-01-01T12:00:05"
    }
  ],
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:05"
}
```

**错误响应**:

**404 Not Found**: 对话不存在
```json
{
  "detail": "对话不存在"
}
```

---

### 5. 删除对话

**DELETE** `/api/conversations/{conversation_id}`

删除指定对话及其所有消息。

**路径参数**:
- `conversation_id`: 对话 ID (UUID)

**响应示例**:
```json
{
  "message": "对话已删除"
}
```

**错误响应**:

**404 Not Found**: 对话不存在
```json
{
  "detail": "对话不存在"
}
```

---

## 使用示例

### Python

#### 流式请求

```python
import requests
import json

def chat_stream(message):
    url = "http://localhost:8000/api/chat"
    data = {"message": message, "stream": True}
    
    response = requests.post(url, json=data, stream=True)
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                chunk = json.loads(line[6:])
                if chunk['type'] == 'content':
                    print(chunk['content'], end='', flush=True)
                elif chunk['type'] == 'done':
                    print(f"\n\n对话 ID: {chunk['conversation_id']}")

chat_stream("请介绍一下 FastAPI")
```

#### 非流式请求

```python
import requests

def chat(message):
    url = "http://localhost:8000/api/chat"
    data = {"message": message, "stream": False}
    
    response = requests.post(url, json=data)
    result = response.json()
    
    print(result['message'])
    return result['conversation_id']

conversation_id = chat("你好")
```

### JavaScript

#### 流式请求 (Fetch)

```javascript
async function chatStream(message) {
  const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, stream: true })
  })
  
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    
    const text = decoder.decode(value)
    const lines = text.split('\n')
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6))
        if (data.type === 'content') {
          console.log(data.content)
        }
      }
    }
  }
}

chatStream('你好')
```

#### 非流式请求 (Axios)

```javascript
import axios from 'axios'

async function chat(message) {
  const response = await axios.post('http://localhost:8000/api/chat', {
    message,
    stream: false
  })
  
  console.log(response.data.message)
  return response.data.conversation_id
}

chat('你好')
```

### cURL

#### 流式请求

```bash
curl -N -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "stream": true}'
```

#### 非流式请求

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "stream": false}'
```

#### 获取对话历史

```bash
curl http://localhost:8000/api/conversations/your-conversation-id
```

#### 删除对话

```bash
curl -X DELETE http://localhost:8000/api/conversations/your-conversation-id
```

---

## 数据模型

### Message (消息)

```typescript
interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string  // ISO 8601 格式
}
```

### ChatRequest (聊天请求)

```typescript
interface ChatRequest {
  message: string              // 必需，1-4000 字符
  conversation_id?: string     // 可选，UUID
  stream?: boolean             // 可选，默认 true
  model?: string               // 可选，默认使用配置的模型
}
```

### ChatResponse (聊天响应)

```typescript
interface ChatResponse {
  conversation_id: string
  message: string
  model: string
  timestamp: string
}
```

### StreamChunk (流式数据块)

```typescript
interface StreamChunk {
  type: 'content' | 'done' | 'error'
  content?: string             // 仅 content 类型
  conversation_id?: string     // 仅 done 类型
  error?: string               // 仅 error 类型
}
```

---

## 速率限制

目前没有实施速率限制。生产环境建议添加：

- 每分钟最多 60 个请求
- 每小时最多 1000 个请求
- 按 IP 或用户限制

---

## 错误代码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 交互式文档

访问 **http://localhost:8000/docs** 查看 Swagger UI 交互式文档。

访问 **http://localhost:8000/redoc** 查看 ReDoc 文档。

---

## 注意事项

1. **消息长度**: 限制为 4000 字符
2. **对话清理**: 超过 1 小时未活动的对话会被自动清理
3. **上下文限制**: 每个对话最多保留最近 10 条消息
4. **流式超时**: 流式请求超时时间为 5 分钟
5. **CORS**: 开发环境已配置 CORS，生产环境需要限制允许的源

---

## 扩展功能（计划）

- [ ] 用户认证和授权
- [ ] 速率限制
- [ ] 对话持久化（数据库）
- [ ] 多模型支持
- [ ] 函数调用
- [ ] 文件上传
- [ ] WebSocket 支持

---

如有问题，请参考主文档或提交 Issue。
