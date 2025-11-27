# 🚀 快速启动指南 - 用户认证版

按照以下步骤快速启动带有用户认证和聊天历史功能的 AI 对话系统。

## ⚡ 5分钟快速启动

### 步骤 1: 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 步骤 2: 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head
```

这将创建以下表：
- ✅ `users` - 用户表
- ✅ `conversations` - 对话表  
- ✅ `messages` - 消息表

### 步骤 3: 配置 JWT 密钥（重要！）

编辑 `backend/.env`，修改以下配置：

```env
# 生成强随机密钥（必须修改！）
JWT_SECRET_KEY=你的超级安全密钥至少32个字符长
```

💡 使用以下命令生成安全密钥：
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 步骤 4: 启动后端

```bash
# 在 backend 目录下
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

看到以下输出表示成功：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 步骤 5: 安装前端依赖

打开新终端：

```bash
cd frontend
npm install
```

### 步骤 6: 启动前端

```bash
npm run dev
```

看到以下输出：
```
  ➜  Local:   http://localhost:5173/
```

### 步骤 7: 访问应用

打开浏览器访问: **http://localhost:5173**

你会看到登录页面！

---

## 📝 首次使用

### 1. 注册账户

- 点击"还没有账户？立即注册"
- 输入邮箱：`test@example.com`
- 输入密码：`password123`
- 确认密码：`password123`
- 点击"注册"

### 2. 开始聊天

注册成功后会自动登录并跳转到主界面：

- 左侧是聊天历史侧边栏
- 右侧是聊天区域
- 底部是输入框

### 3. 发送第一条消息

在输入框输入：`你好，请介绍一下自己`

AI 会流式返回回复，消息会自动保存！

### 4. 管理对话

- **新建对话**: 点击侧边栏顶部的"新建对话"按钮
- **查看历史**: 侧边栏显示所有对话列表
- **搜索对话**: 使用搜索框查找特定对话
- **重命名**: 悬停对话项，点击铅笔图标
- **删除**: 悬停对话项，点击垃圾桶图标

---

## 🔍 验证功能

### 验证 API

打开新终端，测试 API：

```bash
# 健康检查
curl http://localhost:8000/api/health

# 查看 API 文档
# 浏览器访问: http://localhost:8000/docs
```

### 验证数据库

```bash
cd backend
sqlite3 data/kimitalk.db

# 查看表
.tables
# 输出: conversations  messages  users  alembic_version

# 查看用户
SELECT * FROM users;

# 退出
.quit
```

---

## 📂 项目结构概览

```
chattalk/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py           # 👤 认证 API
│   │   │   ├── conversations.py  # 💬 对话管理
│   │   │   └── chat.py           # 🤖 聊天接口
│   │   ├── core/
│   │   │   ├── auth.py           # 🔐 JWT 工具
│   │   │   └── database.py       # 💾 数据库配置
│   │   └── models/
│   │       ├── db_models.py      # 📊 数据库模型
│   │       └── schemas.py        # 📋 API 模型
│   ├── alembic/                  # 🔄 数据库迁移
│   ├── data/                     # 💾 SQLite 数据库
│   └── .env                      # ⚙️ 环境配置
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ChatSidebar.vue   # 📂 侧边栏
    │   │   └── ChatContainer.vue # 💬 聊天区域
    │   ├── views/
    │   │   ├── LoginView.vue     # 🔐 登录页
    │   │   └── MainView.vue      # 🏠 主界面
    │   ├── stores/
    │   │   ├── userStore.js      # 👤 用户状态
    │   │   └── conversationStore.js # 💬 对话状态
    │   └── router/
    │       └── index.js          # 🛣️ 路由配置
    └── package.json
```

---

## 🔧 常见问题

### Q1: 无法启动后端

**错误**: `ModuleNotFoundError: No module named 'bcrypt'`

**解决**:
```bash
pip install -r requirements.txt
```

### Q2: 数据库错误

**错误**: `sqlalchemy.exc.OperationalError: no such table: users`

**解决**:
```bash
alembic upgrade head
```

### Q3: 前端无法连接后端

**错误**: 浏览器控制台显示 `ERR_CONNECTION_REFUSED`

**解决**:
1. 确保后端已启动
2. 检查后端地址是否为 `http://localhost:8000`
3. 检查 CORS 配置

### Q4: Token 认证失败

**错误**: `401 Unauthorized`

**解决**:
1. 检查 `.env` 中的 `JWT_SECRET_KEY` 是否配置
2. 重新登录获取新 Token
3. 检查浏览器 localStorage 中是否有 token

### Q5: 前端依赖安装失败

**错误**: `npm install` 失败

**解决**:
```bash
# 清除缓存
npm cache clean --force

# 删除 node_modules
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

---

## 🎯 下一步

### 学习更多

- 📖 [完整功能文档](AUTH_FEATURES_README.md)
- 🚀 [部署指南](docs/AUTH_DEPLOYMENT.md)
- 📚 [用户指南](docs/USER_GUIDE.md)
- 🔄 [数据库迁移](backend/DATABASE_MIGRATION.md)

### 自定义配置

#### 修改 Token 过期时间

编辑 `backend/.env`:
```env
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 1天
```

#### 修改上下文消息数量

编辑 `backend/.env`:
```env
MAX_CONTEXT_MESSAGES=20  # 保留最近20条消息
```

#### 修改 API 模型

编辑 `backend/.env`:
```env
KIMI_MODEL=moonshot-v1-32k  # 使用 32k 上下文模型
```

---

## 🧪 测试 API

### 使用 curl

```bash
# 1. 注册用户
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 保存返回的 access_token

# 2. 创建对话
curl -X POST http://localhost:8000/api/conversations/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <你的token>" \
  -d '{"title":"测试对话"}'

# 3. 获取对话列表
curl http://localhost:8000/api/conversations/ \
  -H "Authorization: Bearer <你的token>"

# 4. 发送聊天消息
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <你的token>" \
  -d '{"message":"你好","stream":false}'
```

### 使用 API 文档

访问交互式 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📊 功能检查清单

启动成功后，请验证以下功能：

- [ ] 用户可以注册账户
- [ ] 用户可以登录
- [ ] 登录后显示主界面
- [ ] 可以发送消息并收到 AI 回复
- [ ] 消息自动保存
- [ ] 侧边栏显示对话列表
- [ ] 可以创建新对话
- [ ] 可以搜索对话
- [ ] 可以重命名对话
- [ ] 可以删除对话
- [ ] 可以切换对话
- [ ] 退出登录后返回登录页
- [ ] 刷新页面保持登录状态

---

## 💡 提示

### 开发建议

1. **使用开发工具**: 安装 Vue DevTools 和 FastAPI 扩展
2. **查看日志**: 后端和前端终端都会显示有用的调试信息
3. **数据库管理**: 使用 SQLite Browser 查看数据库内容
4. **API 测试**: 使用 Postman 或 Insomnia 测试 API

### 性能优化

1. **生产构建**: 使用 `npm run build` 构建优化的前端
2. **Gunicorn**: 生产环境使用 Gunicorn + Uvicorn workers
3. **Nginx**: 配置反向代理和静态文件服务
4. **数据库索引**: 已在用户邮箱和对话 user_id 上创建索引

---

## 🎓 学习路径

### 初级用户
1. ✅ 完成快速启动
2. 📖 阅读用户指南
3. 🧪 尝试所有功能

### 高级用户
1. 📚 学习完整功能文档
2. 🔧 自定义配置
3. 🚀 部署到生产环境

### 开发者
1. 📖 阅读设计文档
2. 🔍 理解代码结构
3. ✏️ 添加新功能
4. 🧪 编写测试

---

## 🆘 获取帮助

遇到问题？

1. **查看文档**: 本项目包含完整的文档
2. **检查日志**: 查看终端输出和日志文件
3. **数据库验证**: 使用 SQLite 命令行工具检查数据
4. **API 测试**: 使用 `/docs` 端点测试 API

---

## 🎉 恭喜！

你已成功启动带有完整用户认证和聊天历史功能的 AI 对话系统！

现在你可以：
- 👤 注册和管理用户账户
- 💬 进行 AI 对话
- 📂 管理聊天历史
- 🔍 搜索历史对话
- 🎨 享受现代化的 UI

**开始探索吧！** 🚀
