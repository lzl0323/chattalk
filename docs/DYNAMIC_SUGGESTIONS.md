# 动态推荐问题系统

## 🌟 新功能

### 1. 动态热点更新
- ✅ 每6小时自动更新技术热点
- ✅ 整合 GitHub Trending（可扩展）
- ✅ 整合 AI 研究趋势（可扩展）
- ✅ 动态生成推荐问题

### 2. 智能问题池
- **动态问题**：10个（每6小时更新）
- **静态问题**：24个（精选内容）
- **总计**：34个问题池
- **去重**：7天内不重复

## 📊 问题来源

### 动态热点（每6小时更新）

```
GitHub Trending:
• AI Agent 开发框架
• Rust 高性能库  
• 边缘计算技术
• WebGPU 图形渲染
• 零知识证明应用
• 分布式系统设计

AI 研究趋势:
• 大模型对齐技术
• 视觉语言模型
• Agent 协作机制
• 知识图谱增强
• 模型压缩量化
• 多模态融合
```

### 静态精选（固定）

```
技术热点:
• GPT-4 vs Claude 3 对比
• Next.js 14 新特性解读
• React 19 Server Components
...（共24个）
```

## 🔄 工作流程

```
用户访问页面
    ↓
调用 /api/suggestions/
    ↓
检查动态热点缓存（6小时有效）
    ├── 缓存有效 → 使用缓存
    └── 缓存过期 → 获取最新热点
            ↓
        更新缓存
    ↓
合并动态(10) + 静态(24) = 34个
    ↓
过滤最近7天推荐过的
    ↓
随机选择4个
    ↓
保存到数据库
    ↓
返回推荐列表
```

## 🚀 扩展真实数据源

### 接入 GitHub Trending API

```python
async def get_github_trending() -> List[str]:
    """从真实 API 获取 GitHub Trending"""
    async with httpx.AsyncClient() as client:
        # 使用第三方 API
        response = await client.get(
            "https://api.gitterapp.com/repositories",
            params={"since": "daily", "language": ""}
        )
        
        data = response.json()
        topics = [repo["name"] for repo in data[:10]]
        return topics
```

### 接入 ArXiv API

```python
async def get_arxiv_trends() -> List[str]:
    """从 ArXiv 获取研究热点"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://export.arxiv.org/api/query",
            params={
                "search_query": "cat:cs.AI",
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "max_results": 10
            }
        )
        
        # 解析 XML 响应
        # 提取论文标题和关键词
        topics = parse_arxiv_response(response.text)
        return topics
```

### 接入 Hacker News API

```python
async def get_hackernews_topics() -> List[str]:
    """从 Hacker News 获取热门话题"""
    async with httpx.AsyncClient() as client:
        # 获取热门故事
        top_stories = await client.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json"
        )
        
        story_ids = top_stories.json()[:10]
        
        topics = []
        for story_id in story_ids:
            story = await client.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            )
            topics.append(story.json()["title"])
        
        return topics
```

## 📈 缓存策略

### 当前配置

```python
class TrendingFetcher:
    CACHE_HOURS = 6  # 缓存6小时
    
    _cache = {
        "trending": [],       # 动态热点
        "research": [],       # 研究趋势
        "last_update": None   # 最后更新时间
    }
```

### 缓存逻辑

```python
# 检查缓存是否有效
cache_age = now() - last_update
if cache_age < 6小时:
    return cached_data

# 缓存过期，获取新数据
new_data = fetch_from_apis()
update_cache(new_data)
return new_data
```

## 🔧 修复解密问题

### 运行修复脚本

```bash
cd backend
python fix_encryption.py
```

### 输出示例

```
找到 2 个模型配置

✅ 配置 1 (DeepSeek) - 解密成功
❌ 配置 2 (GPT-4) - 解密失败: 解密失败: 

发现 1 个无法解密的配置:
  - ID 2: GPT-4 (gpt-4)

建议删除这些配置，然后重新添加。

是否删除有问题的配置? (yes/no): yes

✅ 已删除配置 2: GPT-4
✅ 成功删除 1 个配置

请到模型管理页面重新添加这些配置。
```

### 重新添加配置

1. 打开模型管理页面：`http://localhost:5173/models`
2. 点击"添加模型"
3. 输入配置信息（API Key 会用当前密钥加密）
4. 保存

## 📊 监控推荐质量

### 查看推荐分布

```python
# 查询最近推荐的问题类型分布
SELECT 
    suggestion_type,
    COUNT(*) as count
FROM suggestion_records
WHERE created_at > DATE('now', '-7 days')
GROUP BY suggestion_type;
```

### 查看最受欢迎的推荐

```python
# 未来实现点击追踪后
SELECT 
    title,
    COUNT(*) as shown_count,
    SUM(is_clicked) as click_count,
    ROUND(SUM(is_clicked) * 100.0 / COUNT(*), 2) as click_rate
FROM suggestion_records
GROUP BY title
ORDER BY click_rate DESC
LIMIT 10;
```

## 🎯 未来优化

### 1. 真实数据源
- [ ] 接入 GitHub Trending API
- [ ] 接入 ArXiv API
- [ ] 接入 Hacker News API
- [ ] 接入技术博客 RSS

### 2. 智能生成
- [ ] 使用 AI 生成更自然的问题
- [ ] 基于用户历史个性化推荐
- [ ] A/B 测试不同推荐策略

### 3. 性能优化
- [ ] 使用 Redis 缓存
- [ ] 后台定时任务更新
- [ ] CDN 缓存推荐数据

### 4. 数据分析
- [ ] 点击率统计
- [ ] 用户偏好分析
- [ ] 推荐质量评估

---

**实现状态**: ✅ 动态热点功能已实现  
**数据源**: 当前使用模拟数据，可扩展真实 API  
**缓存策略**: 6小时自动刷新  
**问题池**: 34个（10动态 + 24静态）
