# ChatGPT 风格前端升级完整指南

## 📋 项目概述

本指南提供将现有 Vue3 聊天应用升级为 ChatGPT 2024 风格 UI 的完整方案。

### 技术栈
- **框架**: Vue 3 + Vite
- **状态管理**: Pinia
- **路由**: Vue Router
- **样式**: Tailwind CSS
- **HTTP**: Axios
- **Markdown**: marked + highlight.js
- **图标**: Heroicons

---

## 🎯 核心功能清单

### ✅ 已实现功能
- [x] 用户注册 / 登录 / Token 鉴权
- [x] 对话历史记录管理
- [x] 流式 SSE 响应
- [x] 模型动态切换
- [x] 模型配额管理
- [x] 自动生成对话标题

### 🎨 新增 UI 功能
- [ ] ChatGPT 风格侧边栏
- [ ] 深色模式切换
- [ ] 消息气泡布局
- [ ] Markdown + 代码高亮
- [ ] 模型配额警告
- [ ] 消息操作（复制/重新生成/删除）
- [ ] 对话搜索
- [ ] 响应式布局

---

## 📦 依赖安装

```bash
cd frontend

# 安装核心依赖
npm install

# 安装新增依赖
npm install @tailwindcss/typography @tailwindcss/forms
npm install marked highlight.js
npm install @vueuse/core
npm install lucide-vue-next
```

---

## 🎨 设计系统

### 颜色方案

#### Light Mode
```
背景: #FFFFFF
侧边栏: #F7F7F8
边框: #E5E5E5
文本主: #2D2E3A
文本次: #6E6E80
强调色: #10A37F (绿色)
```

#### Dark Mode
```
背景: #202123
侧边栏: #343541
边框: #565869
文本主: #ECECF1
文本次: #C5C5D2
强调色: #10A37F (绿色)
```

### 间距系统
```
xs: 0.25rem (4px)
sm: 0.5rem (8px)
md: 1rem (16px)
lg: 1.5rem (24px)
xl: 2rem (32px)
```

### 圆角
```
sm: 0.375rem (6px)
md: 0.5rem (8px)
lg: 0.75rem (12px)
xl: 1rem (16px)
full: 9999px
```

---

## 📁 核心组件架构

### 1. 布局组件

#### `AppLayout.vue` - 主布局
```
┌─────────────────────────────────────┐
│ ┌─────────┬──────────────────────┐  │
│ │         │                      │  │
│ │ Sidebar │    Main Content      │  │
│ │         │                      │  │
│ │         │                      │  │
│ └─────────┴──────────────────────┘  │
└─────────────────────────────────────┘
```

功能：
- 响应式布局（移动端折叠侧边栏）
- 主题切换
- 全局 Toast 通知
- 模态框容器

---

### 2. 侧边栏组件 `Sidebar.vue`

#### 结构
```
┌─────────────────┐
│ [+ 新建聊天]    │
├─────────────────┤
│ 🔍 搜索...      │
├─────────────────┤
│ 📝 聊天记录1    │
│ 📝 聊天记录2    │
│ 📝 聊天记录3    │
│ ...             │
├─────────────────┤
│ ⚙️  设置        │
│ 👤 个人资料     │
│ 🔧 模型管理     │
│ 🌙 深色模式     │
└─────────────────┘
```

#### 功能特性
1. **新建聊天按钮**
   - 固定在顶部
   - 点击创建新对话
   - 快捷键: Ctrl+Shift+N

2. **搜索框**
   - 实时过滤对话列表
   - 支持标题和内容搜索

3. **对话列表**
   - 无限滚动加载
   - 鼠标悬停显示操作按钮
   - 操作：重命名、删除、置顶

4. **底部菜单**
   - 设置
   - 个人资料
   - 模型管理（管理员）
   - 主题切换

---

### 3. 聊天页面 `ChatView.vue`

#### 布局
```
┌──────────────────────────────────────┐
│ 当前对话标题 ✏️         [模型选择] ▼ │
├──────────────────────────────────────┤
│                                      │
│  用户消息 →                          │
│                                      │
│          ← AI 消息                    │
│                                      │
│  用户消息 →                          │
│                                      │
│          ← AI 消息 [复制] [重试] [删]│
│                                      │
├──────────────────────────────────────┤
│ [📎]  输入消息...              [发送]│
└──────────────────────────────────────┘
```

#### 功能特性
1. **顶部栏**
   - 显示当前对话标题（可编辑）
   - 模型选择下拉框
   - 配额显示

2. **消息区域**
   - 自动滚动到底部
   - Markdown 渲染
   - 代码高亮 + 复制按钮
   - 流式打字效果

3. **输入框**
   - 多行支持（Shift+Enter 换行）
   - Enter 发送
   - 文件上传（预留）
   - 字符计数

---

### 4. 消息组件 `ChatMessage.vue`

#### 用户消息
```
┌──────────────────────────┐
│  👤 用户消息内容         │
│     显示在右侧           │
│     灰色背景             │
└──────────────────────────┘
```

#### AI 消息
```
┌──────────────────────────┐
│  🤖 AI 消息内容          │
│     显示在左侧           │
│     透明背景             │
│     [复制] [重试] [删除] │
└──────────────────────────┘
```

#### 特性
- Markdown 完整支持
- 代码块语法高亮
- 表格渲染
- LaTeX 数学公式（可选）
- 图片预览

---

### 5. 模型选择器 `ModelSelector.vue`

#### 下拉列表
```
┌─────────────────────────────┐
│ GPT-4          ✓           │ ← 当前选中
│ 剩余: 50,000 tokens        │
├─────────────────────────────┤
│ Claude-3                    │
│ 剩余: 30,000 tokens        │
├─────────────────────────────┤
│ DeepSeek-V2                 │
│ 剩余: 0 tokens     ❌      │ ← 已禁用
└─────────────────────────────┘
```

#### 功能
- 显示所有可用模型
- 实时配额显示
- 用尽模型禁用 + 红色标记
- 切换时自动保存

---

### 6. 配额警告 `QuotaWarning.vue`

#### 警告横幅
```
┌─────────────────────────────────────┐
│ ⚠️ 当前模型流量已用完，请切换模型  │
│                          [切换] [x] │
└─────────────────────────────────────┘
```

出现时机：
- 模型配额 ≤ 0
- 请求被拒绝（429）
- 固定在顶部，可关闭

---

## 🔧 Pinia Store 架构

### 1. `authStore.js` - 用户认证

```javascript
state: {
  user: null,           // 用户信息
  token: null,          // JWT Token
  isAuthenticated: false
}

actions: {
  login(email, password)
  register(email, password)
  logout()
  refreshToken()
  checkAuth()           // 检查登录状态
}
```

### 2. `chatStore.js` - 聊天管理

```javascript
state: {
  conversations: [],    // 对话列表
  currentConversation: null,
  messages: [],         // 当前消息
  isStreaming: false,
  searchQuery: ''
}

actions: {
  fetchConversations()
  createConversation()
  loadConversation(id)
  updateConversationTitle(id, title)
  deleteConversation(id)
  sendMessage(content)
  streamMessage(content)
  regenerateMessage(messageId)
}

getters: {
  filteredConversations  // 搜索过滤
}
```

### 3. `modelStore.js` - 模型管理

```javascript
state: {
  models: [],           // 所有模型
  selectedModel: null,  // 当前选中
  isLoading: false
}

actions: {
  fetchModels()
  selectModel(id)
  checkQuota(modelId)
}

getters: {
  availableModels,     // 可用模型（配额>0）
  unavailableModels,   // 不可用模型
  currentQuota         // 当前配额
}
```

### 4. `themeStore.js` - 主题管理

```javascript
state: {
  theme: 'light'        // 'light' | 'dark'
}

actions: {
  toggleTheme()
  setTheme(theme)
  loadTheme()           // 从 localStorage 加载
}
```

---

## 🎬 关键交互流程

### 1. 用户登录流程

```
1. 用户输入邮箱密码
   ↓
2. 调用 authStore.login()
   ↓
3. 后端验证并返回 Token
   ↓
4. 保存 Token 到 localStorage
   ↓
5. 设置 Axios 默认 Header
   ↓
6. 加载用户对话列表
   ↓
7. 跳转到聊天页面
```

### 2. 发送消息流程

```
1. 用户输入消息并发送
   ↓
2. 检查模型配额
   ├─ 配额充足 → 继续
   └─ 配额不足 → 显示警告并阻止
   ↓
3. 添加用户消息到界面
   ↓
4. 调用 chatStore.streamMessage()
   ↓
5. 建立 SSE 连接
   ↓
6. 接收流式响应
   ├─ type: content → 追加内容
   ├─ type: suggestions → 显示推荐
   └─ type: done → 完成并保存
   ↓
7. 更新对话标题（如果是第一条）
   ↓
8. 滚动到底部
```

### 3. 切换模型流程

```
1. 用户点击模型选择器
   ↓
2. 显示下拉列表
   ├─ 可用模型: 正常显示
   └─ 不可用模型: 禁用 + 红色标记
   ↓
3. 用户选择新模型
   ↓
4. 调用 modelStore.selectModel()
   ↓
5. 检查配额
   ├─ 配额充足 → 保存选择
   └─ 配额不足 → 显示警告
   ↓
6. 更新 UI 显示
```

---

## 🎨 响应式设计

### 断点
```
sm: 640px   // 小屏幕
md: 768px   // 平板
lg: 1024px  // 笔记本
xl: 1280px  // 桌面
2xl: 1536px // 大屏
```

### 布局适配

#### 桌面 (lg+)
```
┌─────────┬──────────────────┐
│         │                  │
│ Sidebar │  Main Content    │
│ (固定)  │  (自适应宽度)    │
│         │                  │
└─────────┴──────────────────┘
宽度: 260px + flex-1
```

#### 平板 (md ~ lg)
```
┌──────────────────────────┐
│ [☰] Header              │
├──────────────────────────┤
│                          │
│   Main Content           │
│   (全宽)                 │
│                          │
└──────────────────────────┘
Sidebar 折叠为抽屉
点击汉堡菜单展开
```

#### 手机 (sm)
```
┌────────────────┐
│ [☰] Header    │
├────────────────┤
│                │
│ Main Content   │
│ (全宽)         │
│                │
├────────────────┤
│  Input固定底部 │
└────────────────┘
```

---

## 🚀 实施步骤

### Phase 1: 基础配置（Day 1）
1. ✅ 更新 Tailwind 配置
2. ✅ 创建主样式文件
3. ⬜ 配置 Vite
4. ⬜ 安装必要依赖

### Phase 2: Store 重构（Day 1-2）
1. ⬜ 创建 themeStore
2. ⬜ 重构 authStore
3. ⬜ 重构 chatStore
4. ⬜ 重构 modelStore

### Phase 3: 布局组件（Day 2-3）
1. ⬜ 创建 AppLayout
2. ⬜ 创建 Sidebar
3. ⬜ 创建 TopBar
4. ⬜ 实现深色模式

### Phase 4: 聊天组件（Day 3-5）
1. ⬜ 重构 ChatView
2. ⬜ 重构 ChatMessage
3. ⬜ 创建 MarkdownRenderer
4. ⬜ 创建 CodeBlock
5. ⬜ 实现消息操作

### Phase 5: 模型组件（Day 5-6）
1. ⬜ 创建 ModelSelector
2. ⬜ 创建 QuotaWarning
3. ⬜ 实现配额检查

### Phase 6: 通用组件（Day 6-7）
1. ⬜ 创建 Modal
2. ⬜ 创建 Toast
3. ⬜ 创建 Button
4. ⬜ 创建 Input

### Phase 7: 优化&测试（Day 7-8）
1. ⬜ 性能优化
2. ⬜ 错误处理
3. ⬜ 全面测试
4. ⬜ 文档补充

---

## 📝 代码示例

接下来我将提供所有核心组件的完整代码。由于代码量较大，我将分多个文件创建。

---

## 🎯 项目文件清单

### 已创建
- [x] `tailwind.config.new.js` - Tailwind 配置
- [x] `main.new.css` - 主样式文件

### 待创建（按优先级）

#### 高优先级
1. Stores (4个文件)
2. 布局组件 (3个文件)
3. 聊天组件 (6个文件)

#### 中优先级
4. 模型组件 (2个文件)
5. 通用组件 (6个文件)
6. 视图页面 (5个文件)

#### 低优先级
7. 工具函数 (3个文件)
8. 配置文件 (2个文件)

---

## ⚠️ 注意事项

1. **CSS 警告**
   - Tailwind 的 `@apply` 等指令在 IDE 中会显示警告
   - 这是正常的，构建时会被正确处理
   - 可以在 IDE 设置中忽略这些警告

2. **后端兼容性**
   - 保持现有 API 接口不变
   - 前端适配后端返回格式
   - 错误处理使用后端定义的错误码

3. **渐进式迁移**
   - 可以逐步替换现有组件
   - 新旧代码可以共存
   - 先完成核心功能，再优化细节

4. **性能考虑**
   - 对话列表使用虚拟滚动（大量数据时）
   - Markdown 渲染使用 web worker（长文本时）
   - 代码高亮延迟加载

---

## 📚 下一步

接下来我将创建所有核心代码文件。请确认是否继续，或者你想先看某个特定组件的实现？

我建议按以下顺序创建：
1. **Stores** - 状态管理基础
2. **AppLayout + Sidebar** - 页面框架
3. **ChatView + ChatMessage** - 核心功能
4. **其他组件** - 补充功能

准备好后我会开始创建所有文件。
