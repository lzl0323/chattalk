# AI 模型配置管理系统 - 完整实现指南

## 📋 概述

已完成的 AI 模型配置管理系统，支持：
- ✅ 动态管理多个 AI 模型配置
- ✅ API Key 加密存储
- ✅ 配额管理和流量控制
- ✅ 自动配额检查
- ✅ 用户友好的前端界面

## 🎯 核心功能

### 1. 模型配置管理
- 创建、编辑、删除模型配置
- 支持任何 OpenAI 兼容的 API（GPT-4, DeepSeek, Kimi 等）
- API Key 使用 AES 加密存储
- 前端只显示 API Key 前 4 位（如 `sk-1234****`）

### 2. 配额管理
- 设置总配额（tokens）
- 自动追踪使用量
- 配额用尽自动禁用模型
- 支持手动重置配额
- 支持 Cron 表达式自动重置（预留）

### 3. 动态模型选择
- 用户聊天时可选择不同模型
- 自动使用默认模型（第一个激活的）
- 实时检查配额和状态
- 配额不足自动提示

## 🗄️ 数据库设计

### model_configs 表

```sql
CREATE TABLE model_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,          -- 展示名称，如 "GPT-4"
    model VARCHAR(100) NOT NULL,                 -- 模型标识，如 "gpt-4"
    api_base VARCHAR(255) NOT NULL,              -- API 地址
    api_key_encrypted TEXT NOT NULL,             -- 加密的 API Key
    description TEXT,                            -- 描述
    quota_limit FLOAT DEFAULT 1000000.0,         -- 配额限制（tokens）
    quota_used FLOAT DEFAULT 0.0,                -- 已使用配额
    quota_reset_cron VARCHAR(50),                -- 重置 Cron
    is_active BOOLEAN DEFAULT TRUE,              -- 是否激活
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 后端实现

### 已创建的文件

#### 1. 加密服务 (`app/core/encryption.py`)
```python
# 功能：
- AES 加密/解密 API Key
- API Key 遮蔽显示
- 基于 PBKDF2 的密钥派生
```

#### 2. 数据库模型 (`app/models/db_models.py`)
```python
class ModelConfig(Base):
    # 字段：id, name, model, api_base, api_key_encrypted...
    # 方法：
    - quota_remaining: 剩余配额属性
    - quota_percentage: 使用百分比属性
    - is_quota_exceeded(): 检查是否用尽
    - increment_quota(tokens): 增加使用量
    - reset_quota(): 重置配额
```

#### 3. Pydantic Schemas (`app/models/schemas.py`)
```python
- ModelConfigCreate: 创建模型配置
- ModelConfigUpdate: 更新模型配置
- ModelConfigOut: 输出模型配置（含遮蔽 Key）
- ModelConfigList: 配置列表
- QuotaResetRequest: 重置配额请求
```

#### 4. 服务层 (`app/services/model_config_service.py`)
```python
class ModelConfigService:
    - create_model_config()
    - get_model_config()
    - get_model_configs()
    - update_model_config()
    - delete_model_config()
    - reset_quota()
    - to_output_schema()
    - get_decrypted_api_key()
```

#### 5. OpenAI 客户端服务 (`app/services/openai_service.py`)
```python
class OpenAIClientService:
    - create_client(): 创建 OpenAI 客户端
    - check_quota(): 检查配额
    - chat_completion(): 调用聊天 API
    - calculate_tokens_from_response(): 计算 token
    - update_quota_usage(): 更新配额使用
    
# 异常：
- ModelQuotaExceeded: 配额用尽
- ModelNotActive: 模型未激活
```

#### 6. API 路由 (`app/api/model_configs.py`)
```python
# 端点：
POST   /api/model-configs/           # 创建
GET    /api/model-configs/           # 列表
GET    /api/model-configs/{id}       # 详情
PUT    /api/model-configs/{id}       # 更新
DELETE /api/model-configs/{id}       # 删除
POST   /api/model-configs/{id}/reset-quota  # 重置配额
GET    /api/model-configs/active/list      # 激活列表
```

#### 7. 更新的聊天 API (`app/api/chat.py`)
```python
# 更新：
- 接受 model_config_id 参数
- 自动获取模型配置
- 配额检查
- 使用 OpenAI 客户端
- 自动更新配额
```

#### 8. 数据库迁移 (`alembic/versions/002_add_model_configs.py`)
```python
# 创建 model_configs 表
# 添加索引
# 插入默认配置
```

## 🎨 前端实现

### 已更新的文件

#### 1. API 服务 (`services/api.js`)
```javascript
// 新增函数：
- getModelConfigs()         // 获取列表
- getActiveModels()         // 获取激活模型
- getModelConfig()          // 获取详情
- createModelConfig()       // 创建
- updateModelConfig()       // 更新
- deleteModelConfig()       // 删除
- resetModelQuota()         // 重置配额

// 更新函数：
- chatStream(message, conversationId, modelConfigId, ...)
  // 添加 modelConfigId 参数
```

### 需要创建的前端组件

#### 1. 模型管理页面 (`views/ModelConfigView.vue`)

**功能需求：**
```
- 显示模型配置列表
- 显示配额使用情况（进度条）
- 创建/编辑/删除模型
- 重置配额按钮
- 启用/禁用开关
- 配额用尽红色警告
```

#### 2. 更新聊天容器 (`components/ChatContainer.vue`)

**需要添加：**
```vue
<script setup>
import { ref, onMounted } from 'vue'
import { getActiveModels } from '../services/api'

// 模型选择
const availableModels = ref([])
const selectedModelId = ref(null)

// 加载激活的模型
onMounted(async () => {
  try {
    availableModels.value = await getActiveModels()
    if (availableModels.value.length > 0) {
      selectedModelId.value = availableModels.value[0].id
    }
  } catch (error) {
    console.error('Failed to load models:', error)
  }
})

// 更新聊天调用
function sendMessage() {
  chatStream(
    userInput.value,
    conversationId.value,
    selectedModelId.value,  // 传递模型 ID
    onChunk,
    onDone,
    onError
  )
}
</script>

<template>
  <!-- 添加模型选择器 -->
  <div class="model-selector">
    <select v-model="selectedModelId">
      <option 
        v-for="model in availableModels" 
        :key="model.id" 
        :value="model.id"
      >
        {{ model.name }} (剩余: {{ model.quota_remaining.toFixed(0) }} tokens)
      </option>
    </select>
  </div>
</template>
```

## 🚀 部署步骤

### 1. 安装依赖

```bash
cd backend
pip install cryptography==41.0.7
pip install openai==1.6.1
```

### 2. 配置环境变量

编辑 `backend/.env`：
```env
# 加密密钥（必须设置！）
ENCRYPTION_KEY=生成一个强随机密钥

# 其他已有配置...
```

生成加密密钥：
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. 运行数据库迁移

```bash
cd backend
alembic upgrade head
```

这会创建 `model_configs` 表并插入一个默认配置。

### 4. 更新默认模型配置

登录后台，更新默认模型的 API Key：

```python
# 或使用 Python 脚本更新
from app.core.encryption import encryption_service
from app.models.db_models import ModelConfig
from app.core.database import SessionLocal

async def update_default_config():
    async with SessionLocal() as db:
        # 获取第一个配置
        config = await db.get(ModelConfig, 1)
        if config:
            # 加密并更新 API Key
            config.api_key_encrypted = encryption_service.encrypt("你的真实API密钥")
            await db.commit()
```

### 5. 启动服务

```bash
# 后端
cd backend
uvicorn app.main:app --reload

# 前端
cd frontend
npm run dev
```

## 📖 API 使用示例

### 创建模型配置

```bash
curl -X POST http://localhost:8000/api/model-configs/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GPT-4",
    "model": "gpt-4",
    "api_base": "https://api.openai.com/v1",
    "api_key": "sk-your-api-key",
    "description": "OpenAI GPT-4 model",
    "quota_limit": 1000000
  }'
```

### 使用指定模型聊天

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "model_config_id": 1,
    "stream": false
  }'
```

### 重置配额

```bash
curl -X POST http://localhost:8000/api/model-configs/1/reset-quota \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quota_used": 0}'
```

## ⚠️ 安全注意事项

### 1. 加密密钥管理
- ❌ 不要在代码中硬编码 `ENCRYPTION_KEY`
- ✅ 使用环境变量
- ✅ 生产环境使用强随机密钥
- ✅ 定期轮换密钥

### 2. API Key 保护
- ✅ 数据库中加密存储
- ✅ 前端只显示遮蔽版本
- ✅ API 响应不返回完整 Key
- ✅ 日志中不记录完整 Key

### 3. 配额限制
- ✅ 自动检查配额
- ✅ 超限自动禁用
- ✅ 429 错误码提示
- ✅ 前端显示剩余配额

## 🔍 故障排查

### 问题 1：加密失败

**错误**: `Failed to decrypt API key`

**解决**：
1. 检查 `ENCRYPTION_KEY` 是否设置
2. 确保密钥未更改（更改后旧数据无法解密）
3. 重新加密 API Key

### 问题 2：配额未更新

**错误**: Token 使用后配额未增加

**解决**：
1. 检查 OpenAI 响应中是否有 `usage` 字段
2. 查看日志中的 token 计算信息
3. 流式响应使用估算（约 1/4 字符数）

### 问题 3：模型无法使用

**错误**: 429 Too Many Requests

**解决**：
1. 检查模型配额是否用尽
2. 手动重置配额
3. 检查 `is_active` 状态
4. 查看数据库中的 `quota_used` 和 `quota_limit`

## 📝 后续开发建议

### 短期（v2.2）
- [ ] 完善前端模型管理页面
- [ ] 添加配额图表统计
- [ ] 支持批量操作
- [ ] 添加模型测试功能

### 中期（v2.3）
- [ ] 实现 Cron 自动重置
- [ ] 添加使用历史记录
- [ ] 支持按时间段查看使用量
- [ ] 邮件提醒配额即将用尽

### 长期（v3.0）
- [ ] 多用户配额隔离
- [ ] 模型负载均衡
- [ ] 智能模型切换
- [ ] 成本分析报表

## 🎉 总结

已完成的核心功能：
- ✅ 完整的后端 API
- ✅ 数据库模型和迁移
- ✅ 加密和安全机制
- ✅ 配额管理和检查
- ✅ OpenAI 客户端集成
- ✅ 前端 API 封装

待完成：
- ⏳ 前端模型管理界面
- ⏳ 聊天界面模型选择器
- ⏳ 配额可视化组件

**版本**: v2.1.0  
**状态**: 后端完成 ✅，前端待完善  
**更新日期**: 2024-11-27
