# 流式处理注意事项

本文档详细说明 AI 对话系统中流式响应的实现细节和注意事项。

## 什么是流式响应

流式响应（Streaming Response）是一种服务器推送技术，允许服务器在数据准备好时立即发送给客户端，而不是等待全部数据准备完毕。

### 优点

1. **更好的用户体验**: 用户可以立即看到 AI 的回复，而不是等待
2. **感知速度更快**: 即使总时间相同，流式输出让用户感觉更快
3. **降低超时风险**: 长响应不会因为等待时间过长而超时
4. **节省资源**: 不需要在内存中缓存完整响应

### 缺点

1. **错误处理复杂**: 流已经开始后，无法修改 HTTP 状态码
2. **调试困难**: 流式数据难以在开发工具中查看
3. **需要特殊配置**: 中间件（如 Nginx）需要禁用缓冲

---

## 技术实现

### 1. 协议选择

#### Server-Sent Events (SSE)

**特点**:
- 单向通信（服务器 → 客户端）
- 基于 HTTP
- 自动重连
- 简单易用

**格式**:
```
data: {"type": "content", "content": "你好"}\n\n
data: {"type": "content", "content": "世界"}\n\n
data: {"type": "done"}\n\n
```

**适用场景**: AI 对话、实时通知、进度更新

#### WebSocket

**特点**:
- 双向通信
- 持久连接
- 更低延迟
- 更复杂

**适用场景**: 实时游戏、多人协作、聊天室

**我们的选择**: SSE，因为 AI 对话是单向流，SSE 更简单。

### 2. 后端实现 (FastAPI)

#### 2.1 使用 StreamingResponse

```python
from fastapi.responses import StreamingResponse

async def generate_stream():
    async for chunk in kimi_service.chat_stream(messages):
        # SSE 格式
        yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
    yield f"data: {json.dumps({'type': 'done'})}\n\n"

return StreamingResponse(
    generate_stream(),
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
    }
)
```

#### 2.2 异步生成器

```python
async def chat_stream(messages: List[Dict]) -> AsyncGenerator[str, None]:
    """流式调用 Kimi API"""
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, json=data) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunk_data = parse_sse_line(line)
                    if chunk_data:
                        yield chunk_data
```

#### 2.3 错误处理

```python
try:
    async for chunk in stream:
        yield chunk
except Exception as e:
    logger.error(f"Stream error: {e}")
    # 通过 SSE 事件发送错误
    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
```

**注意**: 
- 流开始后无法修改 HTTP 状态码
- 错误必须通过流式事件传递
- 客户端需要监听错误事件

### 3. 前端实现 (Vue3)

#### 3.1 使用 Fetch API

```javascript
async function chatStream(message, onChunk, onDone, onError) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, stream: true })
  })
  
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    
    const text = decoder.decode(value, { stream: true })
    parseSSE(text, onChunk, onDone, onError)
  }
}
```

#### 3.2 SSE 解析

```javascript
let buffer = ''

function parseSSE(text, onChunk, onDone, onError) {
  buffer += text
  const lines = buffer.split('\n')
  buffer = lines.pop() // 保留不完整的行
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6))
      
      if (data.type === 'content') {
        onChunk(data.content)
      } else if (data.type === 'done') {
        onDone(data.conversation_id)
      } else if (data.type === 'error') {
        onError(new Error(data.error))
      }
    }
  }
}
```

#### 3.3 使用 EventSource (替代方案)

```javascript
// 仅适用于 GET 请求
const eventSource = new EventSource('/api/chat?message=hello')

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  handleChunk(data)
}

eventSource.onerror = (error) => {
  eventSource.close()
  handleError(error)
}
```

**限制**: EventSource 只支持 GET 请求，不适合发送复杂数据。

### 4. Nginx 配置

**关键配置**:

```nginx
location /api/ {
    proxy_pass http://backend;
    
    # 禁用缓冲 - 最重要！
    proxy_buffering off;
    proxy_cache off;
    
    # 保持连接
    proxy_http_version 1.1;
    proxy_set_header Connection '';
    
    # 禁用分块传输编码
    chunked_transfer_encoding off;
    
    # 增加超时时间
    proxy_read_timeout 300s;
}
```

**为什么需要禁用缓冲？**

默认情况下，Nginx 会缓冲后端响应，等待完整响应后再发送给客户端。这会破坏流式传输的实时性。

---

## 常见问题

### 1. 流式响应卡住或延迟

**原因**:
- Nginx 缓冲未禁用
- 代理服务器缓冲响应
- 网络问题

**解决**:
```nginx
# Nginx
proxy_buffering off;
proxy_cache off;
```

```python
# FastAPI - 添加头部
headers={
    "X-Accel-Buffering": "no"  # 告诉 Nginx 不要缓冲
}
```

### 2. 流式响应突然中断

**原因**:
- 超时设置过短
- 网络不稳定
- 后端异常

**解决**:
```nginx
# 增加超时时间
proxy_read_timeout 300s;
proxy_send_timeout 300s;
```

```python
# httpx 客户端增加超时
client = httpx.AsyncClient(timeout=300.0)
```

### 3. 无法捕获错误

**问题**: 流已经开始（HTTP 200），后续错误无法通过状态码传递。

**解决**: 通过流式事件传递错误

```python
# 后端
yield f"data: {json.dumps({'type': 'error', 'message': 'xxx'})}\n\n"

# 前端
if (data.type === 'error') {
    onError(new Error(data.message))
}
```

### 4. 浏览器不支持

**检查浏览器兼容性**:
- Fetch API: 现代浏览器均支持
- EventSource: IE 不支持

**降级方案**:
```javascript
if (!window.ReadableStream) {
    // 使用非流式请求
    const response = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message, stream: false })
    })
    const data = await response.json()
    onDone(data.message)
}
```

### 5. CORS 问题

**症状**: 跨域请求失败

**解决**:
```python
# FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # 重要！
)
```

### 6. 流式数据丢失

**原因**: 缓冲区管理不当

**解决**:
```javascript
let buffer = ''

// 正确处理不完整的行
const lines = buffer.split('\n')
buffer = lines.pop()  // 保留最后一个不完整的行

for (const line of lines) {
    // 处理完整的行
}
```

---

## 性能优化

### 1. 连接复用

```python
# 复用 HTTP 客户端
class KimiService:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=300.0,
            limits=httpx.Limits(max_keepalive_connections=20)
        )
```

### 2. 并发控制

```python
# 限制同时处理的流式请求数量
from asyncio import Semaphore

semaphore = Semaphore(10)

async def handle_stream():
    async with semaphore:
        # 处理流式请求
        pass
```

### 3. 内存管理

```python
# 避免在内存中累积完整响应
async def generate_stream():
    async for chunk in source:
        yield chunk  # 立即 yield，不保存
        # 错误做法: buffer.append(chunk)
```

### 4. 超时处理

```python
import asyncio

async def generate_with_timeout():
    try:
        async with asyncio.timeout(300):
            async for chunk in source:
                yield chunk
    except asyncio.TimeoutError:
        yield error_event("请求超时")
```

---

## 调试技巧

### 1. 查看原始 SSE 数据

```bash
# 使用 curl
curl -N http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "stream": true}'
```

### 2. 浏览器开发工具

- Chrome DevTools → Network → 选择请求 → Response
- 查看 EventStream 类型的响应

### 3. 日志记录

```python
# 后端
logger.info(f"Sending chunk: {chunk[:50]}...")  # 记录前 50 字符

# 前端
console.log('Received chunk:', data)
```

### 4. 本地测试

```python
# 创建测试端点
@app.get("/test-stream")
async def test_stream():
    async def generate():
        for i in range(10):
            yield f"data: {i}\n\n"
            await asyncio.sleep(0.5)
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## 最佳实践

### 1. 总是设置正确的 Content-Type

```python
media_type="text/event-stream"
```

### 2. 添加心跳保持连接

```python
async def generate_with_heartbeat():
    last_time = time.time()
    async for chunk in source:
        yield chunk
        last_time = time.time()
    
    # 如果超过 30 秒无数据，发送心跳
    while time.time() - last_time > 30:
        yield ": heartbeat\n\n"
        await asyncio.sleep(30)
```

### 3. 优雅关闭

```javascript
// 前端
const controller = new AbortController()

fetch(url, { signal: controller.signal })

// 需要时取消
controller.abort()
```

### 4. 提供非流式备选方案

```python
@app.post("/chat")
async def chat(request: ChatRequest):
    if request.stream:
        return StreamingResponse(generate_stream())
    else:
        # 非流式响应
        result = await generate_full_response()
        return {"message": result}
```

### 5. 监控和日志

```python
# 记录流式请求指标
logger.info(
    "Stream completed",
    extra={
        "conversation_id": conv_id,
        "duration": duration,
        "chunks_sent": chunk_count
    }
)
```

---

## 安全考虑

### 1. 速率限制

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat")
@limiter.limit("10/minute")
async def chat():
    ...
```

### 2. 超时保护

```python
# 防止恶意客户端长时间占用连接
async with asyncio.timeout(300):
    async for chunk in stream:
        yield chunk
```

### 3. 输入验证

```python
# 验证消息长度
if len(message) > 4000:
    raise ValueError("消息过长")
```

---

## 总结

流式响应是现代 AI 应用的重要特性，但实现时需要注意：

1. **协议选择**: SSE 适合单向流
2. **禁用缓冲**: Nginx 和代理配置
3. **错误处理**: 通过事件传递错误
4. **超时设置**: 合理的超时时间
5. **内存管理**: 避免累积数据
6. **调试工具**: curl、日志、开发工具
7. **降级方案**: 提供非流式备选

遵循这些最佳实践，可以构建稳定、高效的流式 AI 对话系统。
