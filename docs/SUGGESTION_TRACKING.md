# 推荐问题追踪系统

## 🎯 功能概述

推荐问题系统现在支持：
1. **自动保存推荐记录** - 每次生成的推荐都会保存到数据库
2. **智能去重** - 避免在7天内推荐相同的问题
3. **点击追踪** - 记录用户是否点击了推荐（待实现）
4. **数据分析** - 可以统计哪些推荐更受欢迎

## 📊 数据库表结构

### `suggestion_records` 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户ID（外键） |
| suggestion_type | String(20) | 推荐类型（trending/research/general/personalized） |
| title | String(100) | 推荐问题标题 |
| icon | String(20) | 图标类型 |
| is_clicked | Boolean | 是否被点击 |
| clicked_at | DateTime | 点击时间 |
| created_at | DateTime | 推荐时间 |

## 🔄 工作流程

### 1. 用户访问页面

```
用户打开聊天页面
    ↓
前端调用 GET /api/suggestions/?count=4
    ↓
后端生成推荐（避免重复）
    ↓
保存到数据库
    ↓
返回推荐列表
    ↓
前端显示推荐卡片
```

### 2. 去重逻辑

```python
# 获取最近7天推荐过的标题
recent_titles = await get_recent_suggestions(user_id, days=7)

# 从问题池中过滤掉已推荐的
available = [s for s in all_suggestions if s["title"] not in recent_titles]

# 随机选择
selected = random.sample(available, count)
```

### 3. 保存记录

```python
# 每次生成推荐后自动保存
await save_suggestions(db, user_id, suggestions)
```

## 📈 数据分析示例

### 查询用户推荐历史

```sql
SELECT 
    suggestion_type,
    title,
    is_clicked,
    created_at
FROM suggestion_records
WHERE user_id = 1
ORDER BY created_at DESC
LIMIT 20;
```

### 统计点击率（待实现）

```sql
SELECT 
    suggestion_type,
    COUNT(*) as total,
    SUM(CASE WHEN is_clicked THEN 1 ELSE 0 END) as clicked,
    ROUND(SUM(CASE WHEN is_clicked THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as click_rate
FROM suggestion_records
GROUP BY suggestion_type;
```

### 热门推荐排行

```sql
SELECT 
    title,
    COUNT(*) as recommend_count,
    SUM(CASE WHEN is_clicked THEN 1 ELSE 0 END) as click_count
FROM suggestion_records
GROUP BY title
ORDER BY click_count DESC
LIMIT 10;
```

## 🚀 部署步骤

### 1. 运行数据库迁移

```bash
cd backend
alembic upgrade head
```

### 2. 重启后端服务

```bash
uvicorn app.main:app --reload
```

### 3. 测试功能

1. 刷新前端页面
2. 查看推荐问题（每次都不同）
3. 多次刷新，观察7天内不重复

## 📊 当前配置

### 推荐问题池

共 **24 个**精选问题：

#### 技术热点（7个）
- GPT-4 vs Claude 3 对比
- Next.js 14 新特性解读
- React 19 Server Components
- Vue 3.4 性能优化技巧
- TypeScript 5.3 新特性
- Rust 在前端的应用
- WebAssembly 实战指南

#### 科研前沿（6个）
- RAG 技术原理与应用
- 多模态 AI 模型详解
- Diffusion Models 工作原理
- LLM 微调最佳实践
- 强化学习在 NLP 中的应用
- 神经网络压缩技术

#### 实用技巧（11个）
- 前端性能优化指南
- 微服务架构设计要点
- Python 异步编程实战
- Docker 容器化部署
- API 设计最佳实践
- 数据库查询优化技巧
- Git 进阶使用技巧
- Nginx 配置优化
- Redis 缓存策略
- 测试驱动开发实践

### 去重策略

- **时间窗口**: 7天
- **范围**: 相同用户
- **匹配**: 精确标题匹配
- **降级**: 如果可选问题不足，重新使用全部问题池

## 🎯 未来扩展

### 点击追踪（下一步）

添加前端点击事件：

```javascript
// 前端 ChatContainer.vue
const handleExampleClick = async (question) => {
  // 发送点击统计
  await trackSuggestionClick(question)
  
  // 正常发送消息
  handleSendMessage(question)
}
```

后端 API：

```python
@router.post("/{suggestion_id}/click")
async def track_click(suggestion_id: int, db: AsyncSession = Depends(get_db)):
    """记录推荐点击"""
    # 更新 is_clicked 和 clicked_at
    pass
```

### 个性化推荐

基于用户历史对话主题生成个性化推荐：

```python
# 分析用户兴趣
interests = analyze_user_interests(user_id)

# 生成个性化推荐
personalized = generate_personalized_suggestions(interests)
```

### A/B 测试

测试不同推荐策略的效果：

```python
# 策略A: 随机推荐
# 策略B: 基于兴趣推荐
# 策略C: 基于热度推荐

# 对比点击率
compare_click_rates(strategy_a, strategy_b, strategy_c)
```

## 📝 维护建议

### 定期清理旧记录

```sql
-- 清理超过30天的记录
DELETE FROM suggestion_records
WHERE created_at < DATE('now', '-30 days');
```

### 监控推荐质量

```sql
-- 检查推荐分布
SELECT 
    suggestion_type,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM suggestion_records), 2) as percentage
FROM suggestion_records
WHERE created_at > DATE('now', '-7 days')
GROUP BY suggestion_type;
```

---

**实现状态**: ✅ 完成  
**数据库迁移**: 待运行  
**测试状态**: 待测试
