# 用户认证与聊天历史功能 - 完整实现文档

## 🎉 功能概览

本项目已完整实现用户认证和聊天历史管理功能，包括：

✅ **用户注册/登录** - 邮箱 + 密码认证，bcrypt 密码哈希  
✅ **JWT Token 认证** - 使用 python-jose，7 天有效期  
✅ **聊天历史记录** - 所有对话自动保存到 SQLite 数据库  
✅ **侧边栏管理** - 对话列表、搜索、创建、重命名、删除  
✅ **数据库设计** - 用户、对话、消息三张表，完整关联  
✅ **前后端分离** - Vue3 + FastAPI，RESTful API  
✅ **响应式UI** - TailwindCSS 现代化设计  

---

## 📂 项目结构

```
chattalk/
├── backend/                         # FastAPI 后端
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py             # ✨ 认证 API (注册/登录/登出)
│   │   │   ├── conversations.py    # ✨ 对话管理 API
│   │   │   └── chat.py             # 🔄 更新：添加认证验证
│   │   ├── core/
│   │   │   ├── auth.py             # ✨ JWT 工具函数
│   │   │   ├── config.py           # 🔄 更新：JWT 配置
│   │   │   └── database.py         # 数据库配置
│   │   ├── models/
│   │   │   ├── db_models.py        # ✨ 数据库模型 (User/Conversation/Message)
│   │   │   └── schemas.py          # ✨ Pydantic 模型
│   │   └── services/
│   │       └── conversation_service.py  # 🔄 更新：支持 user_id
│   ├── alembic/                     # ✨ 数据库迁移
│   │   ├── versions/
│   │   │   └── 001_initial_migration.py
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── requirements.txt             # 🔄 更新：添加认证依赖
│   ├── alembic.ini                  # ✨ Alembic 配置
│   └── DATABASE_MIGRATION.md        # ✨ 迁移文档
│
├── frontend/                        # Vue3 前端
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatSidebar.vue     # ✨ 聊天历史侧边栏
│   │   │   ├── ChatListItem.vue    # ✨ 对话列表项
│   │   │   └── ChatContainer.vue   # 🔄 更新：支持 conversationId prop
│   │   ├── views/
│   │   │   ├── LoginView.vue       # ✨ 登录/注册页面
│   │   │   └── MainView.vue        # ✨ 主界面（侧边栏 + 聊天）
│   │   ├── stores/
│   │   │   ├── userStore.js        # ✨ 用户状态管理
│   │   │   └── conversationStore.js # ✨ 对话状态管理
│   │   ├── router/
│   │   │   └── index.js            # ✨ Vue Router 配置
│   │   ├── services/
│   │   │   └── api.js              # 🔄 更新：认证拦截器 + 新 API
│   │   ├── App.vue                 # 🔄 更新：router-view
│   │   └── main.js                 # 🔄 更新：注册路由
│   └── package.json                # 🔄 更新：添加 vue-router
│
└── docs/
    ├── AUTH_DEPLOYMENT.md           # ✨ 部署指南
    └── USER_GUIDE.md                # ✨ 用户指南
```

---

## 🗄️ 数据库设计

### ERD 关系图

```
┌─────────────────┐
│     users       │
├─────────────────┤
│ id (PK)         │
│ email (unique)  │
│ hashed_password │
│ is_active       │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────────┐
│  conversations      │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK)        │◄─── 关联用户
│ title               │
│ created_at          │
│ updated_at          │
└────────┬────────────┘
         │ 1
         │
         │ N
┌────────▼────────────┐
│     messages        │
├─────────────────────┤
│ id (PK)             │
│ conversation_id (FK)│◄─── 关联对话
│ role                │ (user/assistant/system)
│ content             │
│ timestamp           │
└─────────────────────┘
```

### 表说明

#### users - 用户表
- 存储用户账户信息
- 密码使用 bcrypt 加密
- 支持激活/禁用状态

#### conversations - 对话表
- 每个对话关联一个用户
- 支持自定义标题
- 自动记录创建和更新时间

#### messages - 消息表
- 存储对话中的所有消息
- role 字段区分用户/助手/系统消息
- 支持时间戳排序

---

## 🔐 认证流程

### 1. 用户注册

```
用户 → POST /api/auth/register
     ├── { email, password }
     │
后端 ├── 1. 验证邮箱格式
     ├── 2. 检查邮箱是否已存在
     ├── 3. 使用 bcrypt 哈希密码
     ├── 4. 创建用户记录
     ├── 5. 生成 JWT Token
     │
     └→ { access_token, token_type, user }
```

### 2. 用户登录

```
用户 → POST /api/auth/login
     ├── { email, password }
     │
后端 ├── 1. 查找用户
     ├── 2. 验证密码（bcrypt.verify）
     ├── 3. 检查用户状态
     ├── 4. 生成 JWT Token
     │
     └→ { access_token, token_type, user }
```

### 3. Token 验证

```
客户端 → 发送请求时在 Header 中添加
        Authorization: Bearer <token>
        │
后端    ├── 1. 解析 JWT Token
        ├── 2. 验证签名和过期时间
        ├── 3. 从 Token 中提取 user_id
        ├── 4. 查询用户是否存在
        │
        └→ 通过验证 → 允许访问资源
           验证失败 → 返回 401 Unauthorized
```

---

## 📡 API 接口

### 认证接口

#### POST /api/auth/register
注册新用户

**请求**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_active": true,
    "created_at": "2024-11-26T21:00:00"
  }
}
```

#### POST /api/auth/login
用户登录

**请求**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**: 同注册

#### GET /api/auth/me
获取当前用户信息（需要认证）

**Headers**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2024-11-26T21:00:00"
}
```

### 对话管理接口

#### POST /api/conversations/
创建新对话

**请求**:
```json
{
  "title": "关于 Python 的讨论"  // 可选
}
```

**响应**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "关于 Python 的讨论",
  "created_at": "2024-11-26T21:00:00",
  "updated_at": "2024-11-26T21:00:00",
  "messages": []
}
```

#### GET /api/conversations/
获取对话列表

**查询参数**:
- `search`: 搜索关键词（可选）
- `limit`: 返回数量（默认 50）
- `offset`: 偏移量（默认 0）

**响应**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "关于 Python 的讨论",
    "created_at": "2024-11-26T21:00:00",
    "updated_at": "2024-11-26T22:00:00",
    "message_count": 5
  }
]
```

#### GET /api/conversations/{conversation_id}
获取对话详情

**响应**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "关于 Python 的讨论",
  "created_at": "2024-11-26T21:00:00",
  "updated_at": "2024-11-26T22:00:00",
  "messages": [
    {
      "role": "user",
      "content": "什么是 Python？",
      "timestamp": "2024-11-26T21:00:00"
    },
    {
      "role": "assistant",
      "content": "Python 是一种高级编程语言...",
      "timestamp": "2024-11-26T21:00:05"
    }
  ]
}
```

#### PUT /api/conversations/{conversation_id}
更新对话标题

**请求**:
```json
{
  "title": "新的标题"
}
```

#### DELETE /api/conversations/{conversation_id}
删除对话

**响应**:
```json
{
  "code": 200,
  "message": "对话已删除",
  "data": {
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### 聊天接口（已更新）

#### POST /api/chat
发送消息（需要认证）

**Headers**:
```
Authorization: Bearer <token>
```

**请求**:
```json
{
  "message": "你好",
  "conversation_id": "550e8400-...",  // 可选
  "stream": true
}
```

**响应**: SSE 流式数据

---

## 🚀 快速开始

### 1. 安装依赖

#### 后端
```bash
cd backend
pip install -r requirements.txt
```

**新增依赖**:
- `bcrypt==4.1.1` - 密码哈希
- `python-jose[cryptography]==3.3.0` - JWT Token
- `passlib==1.7.4` - 密码验证

#### 前端
```bash
cd frontend
npm install
```

**新增依赖**:
- `vue-router@^4.2.5` - 路由管理

### 2. 配置环境变量

编辑 `backend/.env`:

```env
# JWT 配置（必须修改！）
JWT_SECRET_KEY=your-very-secure-secret-key-min-32-characters
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7天

# 其他配置...
KIMI_API_KEY=你的API密钥
```

⚠️ **重要**：生产环境必须使用强随机密钥！

生成密钥：
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. 初始化数据库

```bash
cd backend
alembic upgrade head
```

### 4. 启动服务

#### 后端
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端
```bash
cd frontend
npm run dev
```

### 5. 访问应用

打开浏览器访问: `http://localhost:5173`

---

## 📝 使用流程

### 用户流程

1. **首次访问** → 显示登录页面
2. **注册账户** → 输入邮箱和密码
3. **自动登录** → 跳转到主界面
4. **开始聊天** → 输入消息，自动保存
5. **查看历史** → 侧边栏显示所有对话
6. **管理对话** → 搜索、重命名、删除

### 开发流程

1. **修改数据模型** → 编辑 `db_models.py`
2. **生成迁移** → `alembic revision --autogenerate -m "说明"`
3. **运行迁移** → `alembic upgrade head`
4. **更新 API** → 修改路由和服务
5. **更新前端** → 修改组件和状态管理

---

## 🔧 关键实现细节

### 1. 密码安全

```python
# app/core/auth.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 2. JWT Token

```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=10080)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 3. 认证依赖

```python
from fastapi import Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    # 验证并返回用户
    return user
```

### 4. 前端拦截器

```javascript
// src/services/api.js
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

### 5. 路由守卫

```javascript
// src/router/index.js
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const authed = isAuthenticated.value

  if (requiresAuth && !authed) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && authed) {
    next({ name: 'Home' })
  } else {
    next()
  }
})
```

---

## 📚 文档索引

- **[部署指南](docs/AUTH_DEPLOYMENT.md)** - 完整的生产环境部署流程
- **[用户指南](docs/USER_GUIDE.md)** - 最终用户使用说明
- **[数据库迁移](backend/DATABASE_MIGRATION.md)** - Alembic 迁移详解
- **[API 文档](docs/API.md)** - 原有 API 文档
- **[设计文档](docs/DESIGN.md)** - 系统架构设计

---

## ✅ 功能清单

### 后端功能

- [x] 用户注册 API
- [x] 用户登录 API
- [x] 获取当前用户 API
- [x] JWT Token 生成与验证
- [x] 密码 bcrypt 哈希
- [x] 创建对话 API
- [x] 获取对话列表 API
- [x] 获取对话详情 API
- [x] 更新对话标题 API
- [x] 删除对话 API
- [x] 聊天接口认证保护
- [x] 数据库模型设计
- [x] Alembic 迁移配置
- [x] 用户与对话数据隔离

### 前端功能

- [x] 登录/注册页面
- [x] 表单验证
- [x] Token 自动存储
- [x] 认证拦截器
- [x] 401 自动跳转登录
- [x] 聊天历史侧边栏
- [x] 对话列表显示
- [x] 搜索对话
- [x] 新建对话
- [x] 重命名对话
- [x] 删除对话
- [x] 对话切换
- [x] 用户状态管理
- [x] 对话状态管理
- [x] 路由守卫
- [x] 响应式布局

---

## 🎯 后续扩展建议

### 短期
1. ✅ 用户认证（已完成）
2. ✅ 聊天历史（已完成）
3. ⏳ 密码重置功能
4. ⏳ 邮箱验证
5. ⏳ 个人资料编辑

### 中期
1. ⏳ 对话分享链接
2. ⏳ 导出对话记录（PDF/Markdown）
3. ⏳ 多模型支持
4. ⏳ 文件上传（图片、文档）
5. ⏳ 语音输入/输出

### 长期
1. ⏳ Redis 缓存
2. ⏳ PostgreSQL 支持
3. ⏳ 多租户架构
4. ⏳ 管理后台
5. ⏳ 数据分析和统计

---

## 🐛 已知问题

暂无已知重大问题。

---

## 📞 技术支持

如遇问题，请：

1. 查看[故障排查](docs/AUTH_DEPLOYMENT.md#故障排查)
2. 检查日志文件
3. 提交 Issue

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- **FastAPI** - 高性能 Python Web 框架
- **Vue.js** - 渐进式 JavaScript 框架
- **TailwindCSS** - 实用优先的 CSS 框架
- **Kimi API** - 强大的 AI 能力

---

**版本**: 2.0.0  
**最后更新**: 2024-11-26  
**状态**: ✅ 生产就绪

🎉 **恭喜！所有功能已完整实现！**
