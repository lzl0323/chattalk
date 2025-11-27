# 更新日志

本文档记录项目的所有重要更改。

---

## [2.0.0] - 2024-11-26

### ✨ 新增功能

#### 用户认证系统
- ✅ 用户注册功能（邮箱 + 密码）
- ✅ 用户登录功能
- ✅ JWT Token 认证（7天有效期）
- ✅ 密码 bcrypt 哈希加密
- ✅ 获取当前用户信息接口
- ✅ 用户登出功能
- ✅ 自动 Token 刷新机制

#### 聊天历史管理
- ✅ 聊天历史侧边栏 UI
- ✅ 对话列表显示（按更新时间排序）
- ✅ 搜索对话功能
- ✅ 新建对话
- ✅ 重命名对话
- ✅ 删除对话
- ✅ 切换对话
- ✅ 当前对话高亮显示
- ✅ 消息数量统计
- ✅ 时间戳显示（智能格式化）

#### 数据持久化
- ✅ SQLite 数据库设计
- ✅ Users 表（用户信息）
- ✅ Conversations 表（对话列表）
- ✅ Messages 表（消息记录）
- ✅ 完整的外键关联
- ✅ 自动保存用户消息
- ✅ 自动保存 AI 回复
- ✅ 对话更新时间自动维护

#### 前端组件
- ✅ LoginView - 登录/注册页面
- ✅ MainView - 主界面布局
- ✅ ChatSidebar - 聊天历史侧边栏
- ✅ ChatListItem - 对话列表项组件
- ✅ Vue Router 路由配置
- ✅ 路由守卫（认证保护）
- ✅ userStore - 用户状态管理
- ✅ conversationStore - 对话状态管理

#### API 接口
- ✅ POST /api/auth/register - 用户注册
- ✅ POST /api/auth/login - 用户登录
- ✅ GET /api/auth/me - 获取当前用户
- ✅ POST /api/auth/logout - 用户登出
- ✅ POST /api/conversations/ - 创建对话
- ✅ GET /api/conversations/ - 获取对话列表
- ✅ GET /api/conversations/{id} - 获取对话详情
- ✅ PUT /api/conversations/{id} - 更新对话标题
- ✅ DELETE /api/conversations/{id} - 删除对话
- ✅ POST /api/conversations/messages - 添加消息

### 🔄 更新内容

#### 后端更新
- 🔄 添加认证依赖（bcrypt, python-jose, passlib）
- 🔄 更新配置支持 JWT 设置
- 🔄 聊天接口添加认证保护
- 🔄 对话服务支持 user_id 参数
- 🔄 数据库模型添加用户关联
- 🔄 API 路由注册新的认证和对话路由
- 🔄 CORS 配置更新

#### 前端更新
- 🔄 添加 vue-router 依赖
- 🔄 API 服务添加认证拦截器
- 🔄 自动添加 Bearer Token
- 🔄 401 错误自动跳转登录
- 🔄 ChatContainer 支持 conversationId prop
- 🔄 ChatContainer 支持 initialMessages prop
- 🔄 App.vue 改用 router-view
- 🔄 main.js 注册路由

### 🗄️ 数据库迁移
- ✅ Alembic 配置文件
- ✅ 初始迁移脚本（001_initial_migration.py）
- ✅ 数据库迁移文档

### 📚 文档新增
- ✅ AUTH_FEATURES_README.md - 完整功能实现文档
- ✅ AUTH_DEPLOYMENT.md - 部署指南
- ✅ USER_GUIDE.md - 用户使用指南
- ✅ DATABASE_MIGRATION.md - 数据库迁移指南
- ✅ QUICKSTART_AUTH.md - 快速启动指南
- ✅ CHANGELOG.md - 本文件

### 🔐 安全性增强
- 🔒 密码 bcrypt 哈希存储
- 🔒 JWT Token 认证
- 🔒 用户数据隔离
- 🔒 API 接口认证保护
- 🔒 HTTPS 支持（生产环境）
- 🔒 安全头配置

### 🎨 UI/UX 改进
- 🎨 现代化登录/注册页面
- 🎨 响应式侧边栏设计
- 🎨 用户头像显示
- 🎨 对话项悬停效果
- 🎨 搜索框设计
- 🎨 加载状态指示
- 🎨 错误提示优化
- 🎨 移动端适配

### 🚀 性能优化
- ⚡ 数据库索引（email, user_id, conversation_id）
- ⚡ API 响应优化
- ⚡ 前端状态管理优化
- ⚡ 组件懒加载

---

## [1.0.0] - 2024-11 (之前)

### 初始功能
- ✅ 基础聊天功能
- ✅ 流式响应支持
- ✅ Kimi API 集成
- ✅ System Prompt 配置
- ✅ Markdown 渲染
- ✅ 消息气泡组件
- ✅ 输入框组件
- ✅ TailwindCSS 样式
- ✅ 示例问题
- ✅ 基础错误处理
- ✅ Nginx 配置
- ✅ 开发环境配置
- ✅ 基础文档

---

## 版本对比

### 1.0.0 vs 2.0.0

| 功能 | v1.0.0 | v2.0.0 |
|------|--------|--------|
| 用户认证 | ❌ | ✅ |
| 聊天历史 | ❌ | ✅ |
| 数据持久化 | ❌ | ✅ |
| 对话管理 | ❌ | ✅ |
| 用户隔离 | ❌ | ✅ |
| 侧边栏 | ❌ | ✅ |
| 搜索功能 | ❌ | ✅ |
| 数据库 | ❌ | ✅ SQLite |
| 安全性 | 基础 | ✅ 增强 |
| 文档完整性 | 基础 | ✅ 完善 |

---

## 迁移指南

### 从 v1.0.0 升级到 v2.0.0

#### 后端迁移

1. **安装新依赖**:
```bash
cd backend
pip install -r requirements.txt
```

2. **配置 JWT**:
编辑 `.env` 添加：
```env
JWT_SECRET_KEY=生成一个强随机密钥
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

3. **初始化数据库**:
```bash
alembic upgrade head
```

4. **重启后端服务**

#### 前端迁移

1. **安装新依赖**:
```bash
cd frontend
npm install
```

2. **无需其他配置**，新功能自动生效

3. **重启前端服务**

#### 数据迁移

⚠️ **重要**: v1.0.0 没有数据持久化，无需数据迁移

---

## 已知问题

### v2.0.0
- ⚠️ 暂不支持密码重置功能
- ⚠️ 暂不支持邮箱验证
- ⚠️ 暂不支持对话导出
- ⚠️ 暂不支持对话分享

---

## 计划功能

### v2.1.0（短期）
- [ ] 密码重置功能
- [ ] 邮箱验证
- [ ] 个人资料编辑
- [ ] 头像上传
- [ ] 对话标签/分类

### v2.2.0（中期）
- [ ] 对话导出（PDF/Markdown）
- [ ] 对话分享链接
- [ ] 多模型支持
- [ ] 文件上传（图片、文档）
- [ ] 主题切换（暗色模式）

### v3.0.0（长期）
- [ ] PostgreSQL 支持
- [ ] Redis 缓存
- [ ] WebSocket 实时通信
- [ ] 多租户架构
- [ ] 管理后台
- [ ] 数据分析和统计
- [ ] 语音输入/输出

---

## 贡献者

感谢所有为本项目做出贡献的开发者！

---

## 反馈

如有任何问题或建议，请：
- 查看文档
- 提交 Issue
- 联系项目维护者

---

**最后更新**: 2024-11-26  
**当前版本**: 2.0.0  
**状态**: ✅ 稳定
