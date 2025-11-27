# AI 对话系统 - 完整开发方案

> 🎉 **v2.0.0 新功能**: 现已支持用户认证和聊天历史管理！  
> 📚 查看 [完整功能文档](../AUTH_FEATURES_README.md) | [快速启动](../QUICKSTART_AUTH.md) | [部署指南](AUTH_DEPLOYMENT.md)

## 项目概述

一个基于 Vue3 + FastAPI + Nginx 的 AI 对话系统，通过 OpenAI-compatible API 访问 Kimi 模型，支持流式响应、用户认证和聊天历史管理。

## 技术栈

- **前端**: Vue3 + Vite + Axios + TailwindCSS
- **后端**: FastAPI + SQLAlchemy + Python 3.11+
- **数据库**: SQLite (异步支持)
- **环境管理**: Conda (推荐) 或 venv
- **代理**: Nginx
- **AI 模型**: Kimi (通过 OpenAI-compatible API)

## 项目结构

```
vue+fastapi/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # 主应用入口
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── chat.py     # 聊天接口
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py   # 配置管理
│   │   │   └── prompts.py  # System Prompt 管理
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── kimi.py     # Kimi API 服务
│   │   └── models/
│   │       ├── __init__.py
│   │       └── schemas.py  # 数据模型
│   ├── requirements.txt     # Python 依赖
│   └── .env.example        # 环境变量示例
├── frontend/               # Vue3 前端
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatMessage.vue     # 消息气泡组件
│   │   │   ├── ChatInput.vue       # 输入框组件
│   │   │   └── ChatContainer.vue   # 聊天容器组件
│   │   ├── services/
│   │   │   └── api.js              # API 服务
│   │   ├── App.vue                  # 根组件
│   │   └── main.js                  # 入口文件
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── nginx/
│   └── nginx.conf          # Nginx 配置
├── docs/
│   ├── DESIGN.md          # 详细设计文档
│   ├── DEPLOYMENT.md      # 部署指南
│   └── STREAM_NOTES.md    # 流式处理注意事项
└── README.md              # 本文件
```

## 核心功能

### 后端 (FastAPI)

1. **流式转发**: 将用户消息转发到 Kimi API，并以 SSE 流式返回
2. **数据持久化**: 使用 SQLite 数据库存储对话历史
3. **上下文管理**: 维护对话历史，支持多轮对话
4. **System Prompt**: 封装专业的 AI 助手行为规范
5. **异常处理**: 完善的错误处理和日志记录
6. **CORS 支持**: 跨域资源共享配置

### 前端 (Vue3)

1. **现代 UI**: 基于 TailwindCSS 的美观聊天界面
2. **流式显示**: 实时显示 AI 回复，逐字渲染
3. **消息管理**: 对话历史展示和管理
4. **响应式设计**: 适配不同屏幕尺寸
5. **加载状态**: 友好的等待和加载提示

### 代理层 (Nginx)

1. **反向代理**: `/api/` 路由到 FastAPI
2. **静态服务**: `/` 服务 Vue3 构建文件
3. **流式支持**: 配置支持 SSE 流式响应
4. **安全设置**: CORS、缓存、压缩等

## 快速开始

> 💡 **推荐使用 Conda**: 查看 [CONDA_QUICKSTART.md](CONDA_QUICKSTART.md) 获取完整的 Conda + SQLite 设置指南

### 方式 1: 使用 Conda (推荐)

```bash
cd backend

# 创建并激活 Conda 环境
conda env create -f environment.yml
conda activate kimitalk

# 启动服务（数据库自动初始化）
start.bat          # Windows
./start.sh         # Linux/Mac
```

### 方式 2: 使用 venv

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量（密钥已配置在 .env）
# 如需修改，编辑 .env 文件

# 初始化数据库
python init_db.py

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端设置

```bash
cd frontend
npm install
npm run dev  # 开发模式
npm run build  # 生产构建
```

### 3. Nginx 配置

```bash
# 将 nginx/nginx.conf 复制到 Nginx 配置目录
# 根据实际路径修改配置文件中的路径
sudo nginx -t  # 测试配置
sudo nginx -s reload  # 重载配置
```

## API 接口

### POST /api/chat

发送消息并接收流式响应。

**请求体**:
```json
{
  "message": "你好",
  "conversation_id": "optional-uuid",
  "stream": true
}
```

**响应**: SSE 流式数据
```
data: {"type": "content", "content": "你"}
data: {"type": "content", "content": "好"}
data: {"type": "done", "conversation_id": "uuid"}
```

## 环境变量

创建 `backend/.env` 文件：

```env
KIMI_API_KEY=sk-MLtlwyjKSv3kbe6jLyFndfCqsHtet4iImwE3M9TVH8p3AU15
KIMI_API_BASE=https://api.moonshot.cn/v1
KIMI_MODEL=moonshot-v1-8k
MAX_CONTEXT_MESSAGES=10
LOG_LEVEL=INFO
```

## 数据库

### SQLite 配置

- **数据库文件**: `backend/data/kimitalk.db`
- **自动创建**: 首次启动时自动初始化
- **ORM**: SQLAlchemy 2.0 (异步)
- **驱动**: aiosqlite

### 数据库表

1. **conversations** - 对话表
   - id (主键)
   - created_at, updated_at

2. **messages** - 消息表
   - id (主键)
   - conversation_id (外键)
   - role (user/assistant/system)
   - content, timestamp

### 数据库操作

```bash
# 手动初始化数据库
python backend/init_db.py

# 查看数据库
cd backend/data
sqlite3 kimitalk.db
.tables
SELECT * FROM conversations;
.quit

# 重置数据库（删除所有数据）
rm backend/data/kimitalk.db  # Linux/Mac
del backend\data\kimitalk.db  # Windows
python backend/init_db.py
```

## 开发指南

### System Prompt 设计

位于 `backend/app/core/prompts.py`，定义 AI 助手的行为规范：

- 角色定位：专业、友好的 AI 助手
- 回答风格：清晰、结构化、使用 Markdown
- 安全规范：拒绝不当请求，保护隐私
- 格式要求：使用标题、列表、代码块

### 流式处理注意事项

1. **后端**: 使用 `StreamingResponse` 和异步生成器
2. **前端**: 使用 `EventSource` 或 `fetch` 处理 SSE
3. **Nginx**: 禁用缓冲以支持实时流式传输
4. **错误处理**: 流式传输中的异常需要通过特殊事件传递

## 部署建议

### 开发环境
- 后端: `uvicorn` 直接运行
- 前端: `npm run dev` 热更新
- 无需 Nginx

### 生产环境
- 后端: `gunicorn` + `uvicorn` workers
- 前端: `npm run build` 构建静态文件
- Nginx: 反向代理 + 静态文件服务 + HTTPS

## 安全建议

1. **API 密钥**: 使用环境变量，不要硬编码
2. **HTTPS**: 生产环境必须使用 HTTPS
3. **速率限制**: 考虑添加 API 调用限流
4. **输入验证**: 验证和清理用户输入
5. **CORS**: 限制允许的源

## 扩展功能

- [x] **用户认证和会话管理** ✅ v2.0.0
- [x] **对话历史持久化（数据库）** ✅ v2.0.0
- [x] **聊天历史侧边栏** ✅ v2.0.0
- [x] **对话搜索和管理** ✅ v2.0.0
- [ ] 多模型切换
- [ ] 文件上传支持
- [ ] 语音输入/输出
- [ ] 分享对话功能
- [ ] 主题切换（暗色/亮色）
- [ ] 导出对话记录

## 故障排查

查看详细的故障排查指南：`docs/DEPLOYMENT.md`

## 许可证

MIT License

## 联系方式

如有问题，请查阅 `docs/` 目录下的详细文档。
