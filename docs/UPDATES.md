# 项目更新说明 - Conda + SQLite 支持

## 🎉 主要更新

### ✨ 新增功能

1. **Conda 环境管理**
   - ✅ 添加 `environment.yml` 配置文件
   - ✅ 自动化设置脚本 (`setup_conda.bat/sh`)
   - ✅ 环境名称: **kimitalk**
   - ✅ Python 版本: 3.11

2. **SQLite 数据库支持**
   - ✅ 数据持久化（对话历史不再丢失）
   - ✅ 异步数据库操作（aiosqlite）
   - ✅ SQLAlchemy 2.0 ORM
   - ✅ 自动初始化和迁移支持（Alembic）

3. **完善的数据库管理**
   - ✅ 对话表 (conversations)
   - ✅ 消息表 (messages)
   - ✅ 外键关联和级联删除
   - ✅ 自动时间戳

4. **新增工具脚本**
   - ✅ `init_db.py` - 数据库初始化
   - ✅ `setup_conda.bat/sh` - Conda 环境设置
   - ✅ 更新的启动脚本（自动数据库检查）

### 📝 新增文档

1. **backend/CONDA_SETUP.md**
   - 详细的 Conda 设置指南
   - 数据库操作说明
   - 故障排查

2. **CONDA_QUICKSTART.md**
   - 一键启动指南
   - 快速命令参考
   - 常见问题解答

3. **UPDATES.md** (本文件)
   - 更新说明
   - 迁移指南

### 🔄 代码更新

#### 后端更新

1. **新增文件**:
   - `app/core/database.py` - 数据库配置
   - `app/models/db_models.py` - 数据库模型
   - `app/services/conversation_service.py` - 对话服务

2. **修改文件**:
   - `app/api/chat.py` - 使用数据库替代内存存储
   - `app/main.py` - 添加数据库初始化
   - `requirements.txt` - 添加数据库依赖

3. **新增依赖**:
   ```
   sqlalchemy==2.0.23
   aiosqlite==0.19.0
   alembic==1.13.0
   ```

#### 配置更新

1. **environment.yml** - Conda 环境配置
2. **.gitignore** - 排除数据库文件
3. **启动脚本** - 自动数据库初始化

---

## 🚀 如何使用新功能

### 选项 1: 使用 Conda（推荐）

```bash
# 1. 创建 Conda 环境
cd backend
conda env create -f environment.yml

# 2. 激活环境
conda activate kimitalk

# 3. 启动（数据库自动初始化）
start.bat  # Windows
./start.sh  # Linux/Mac
```

### 选项 2: 继续使用 venv

```bash
# 1. 激活 venv
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装新依赖
pip install -r requirements.txt

# 3. 初始化数据库
python init_db.py

# 4. 启动服务
uvicorn app.main:app --reload
```

---

## 🔄 从旧版本迁移

### 如果你之前使用的是内存存储版本

**好消息**: 无需额外操作！

新版本会自动：
1. 在首次启动时创建数据库
2. 初始化表结构
3. 开始持久化对话

**注意**:
- 之前的对话历史不会迁移（因为是存在内存中的）
- 第一次启动可能会多花几秒钟初始化数据库

### 如果你已经有正在运行的实例

```bash
# 1. 停止服务
# Ctrl+C

# 2. 安装新依赖
pip install sqlalchemy aiosqlite alembic

# 3. 初始化数据库
python init_db.py

# 4. 重启服务
uvicorn app.main:app --reload
```

---

## 📊 功能对比

### 旧版本 vs 新版本

| 特性 | 旧版本（内存） | 新版本（SQLite） |
|------|---------------|------------------|
| 数据持久化 | ❌ 重启丢失 | ✅ 永久保存 |
| 并发支持 | ⚠️ 有限 | ✅ 更好 |
| 查询能力 | ❌ 基本遍历 | ✅ SQL 查询 |
| 内存占用 | ⚠️ 随对话增加 | ✅ 稳定 |
| 适用场景 | 测试/演示 | ✅ 生产环境 |
| 数据分析 | ❌ 困难 | ✅ 容易 |
| 备份恢复 | ❌ 不可能 | ✅ 复制文件即可 |

---

## 🗄️ 数据库详情

### 文件位置

```
backend/
├── data/
│   ├── kimitalk.db      # SQLite 数据库文件
│   └── .gitkeep         # Git 目录占位符
```

### 表结构

#### conversations 表

```sql
CREATE TABLE conversations (
    id VARCHAR(36) PRIMARY KEY,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

#### messages 表

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id VARCHAR(36) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (conversation_id) 
        REFERENCES conversations(id) 
        ON DELETE CASCADE
);
```

### 数据示例

查看存储的对话：

```bash
cd backend/data
sqlite3 kimitalk.db

# 查看对话数量
SELECT COUNT(*) FROM conversations;

# 查看最近的对话
SELECT c.id, c.created_at, COUNT(m.id) as message_count
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
GROUP BY c.id
ORDER BY c.updated_at DESC
LIMIT 10;

# 查看特定对话的消息
SELECT role, content, timestamp
FROM messages
WHERE conversation_id = 'your-conversation-id'
ORDER BY timestamp;
```

---

## 🔧 故障排查

### 问题：数据库文件无法创建

**症状**: 启动时报错 "Unable to create database file"

**解决方案**:
```bash
# 确保 data 目录存在且有写权限
mkdir -p backend/data
chmod 755 backend/data  # Linux/Mac
```

### 问题：SQLAlchemy 导入错误

**症状**: "No module named 'sqlalchemy'"

**解决方案**:
```bash
# 确保激活了正确的环境
conda activate kimitalk  # 或 source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
```

### 问题：数据库被锁定

**症状**: "database is locked"

**解决方案**:
```bash
# 1. 停止所有正在运行的实例
# 2. 删除数据库锁文件（如果存在）
rm backend/data/kimitalk.db-shm
rm backend/data/kimitalk.db-wal
# 3. 重启服务
```

### 问题：想要重置数据库

**解决方案**:
```bash
# 停止服务
# Ctrl+C

# 删除数据库文件
rm backend/data/kimitalk.db  # Linux/Mac
del backend\data\kimitalk.db  # Windows

# 重新初始化
python backend/init_db.py

# 重启服务
```

---

## 📈 性能提升

### 内存使用

- **旧版本**: 随对话数量线性增长
- **新版本**: 稳定（仅缓存当前操作）

### 响应速度

- **旧版本**: 内存查找（极快）
- **新版本**: 数据库查询（仍然很快，<10ms）

### 并发处理

- **旧版本**: 单线程内存操作
- **新版本**: 异步数据库连接池

---

## 🎓 学习资源

### SQLAlchemy

- 官方文档: https://docs.sqlalchemy.org/
- 异步教程: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

### SQLite

- 官方文档: https://www.sqlite.org/
- Python SQLite: https://docs.python.org/3/library/sqlite3.html

### Conda

- 用户指南: https://docs.conda.io/projects/conda/en/latest/user-guide/
- 环境管理: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html

---

## 🔮 未来计划

### 短期（已实现）

- [x] SQLite 数据库支持
- [x] Conda 环境管理
- [x] 自动数据库初始化
- [x] 完善的文档

### 中期

- [ ] 用户认证系统
- [ ] Redis 缓存层
- [ ] PostgreSQL 支持（可选）
- [ ] 数据导出功能

### 长期

- [ ] 分布式部署
- [ ] 实时协作
- [ ] 高级分析功能
- [ ] 云端同步

---

## ✅ 验证清单

完成更新后，请验证：

- [ ] Conda 环境已创建 (`conda env list`)
- [ ] 数据库文件已创建 (`ls backend/data/`)
- [ ] 后端可以正常启动
- [ ] 可以发送消息并收到回复
- [ ] 对话历史持久化（重启后仍然存在）
- [ ] API 文档可访问 (http://localhost:8000/docs)
- [ ] 健康检查显示数据库信息

---

## 📞 获取帮助

如有问题：

1. 查看 `backend/CONDA_SETUP.md`
2. 查看 `CONDA_QUICKSTART.md`
3. 查看 `docs/DEPLOYMENT.md`
4. 检查日志输出
5. 提交 Issue

---

**更新日期**: 2024-11-26  
**版本**: 2.0.0 (添加数据库支持)

感谢使用！🎉
