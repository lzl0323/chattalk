# Conda 环境设置指南

本指南说明如何使用 Conda 管理 Python 环境并配置 SQLite 数据库。

## 📋 前置要求

- **Conda**: Anaconda 或 Miniconda
  - 下载 Miniconda: https://docs.conda.io/en/latest/miniconda.html
  - 下载 Anaconda: https://www.anaconda.com/download

## 🚀 快速开始

### Windows

```cmd
cd E:\PROJECT-lzl\vue+fastapi\backend
setup_conda.bat
```

### Linux/Mac

```bash
cd /path/to/vue+fastapi/backend
chmod +x setup_conda.sh
./setup_conda.sh
```

## 📝 手动设置步骤

### 1. 创建 Conda 环境

使用 `environment.yml` 文件创建环境：

```bash
conda env create -f environment.yml
```

这将创建一个名为 **kimitalk** 的环境，包含：
- Python 3.11
- FastAPI 和相关依赖
- SQLAlchemy（数据库 ORM）
- aiosqlite（异步 SQLite 驱动）
- Alembic（数据库迁移工具）

### 2. 激活环境

```bash
# Windows
conda activate kimitalk

# Linux/Mac
conda activate kimitalk
```

### 3. 验证安装

```bash
python --version
# 应输出: Python 3.11.x

pip list | grep -i fastapi
# 应看到 fastapi、sqlalchemy 等包
```

### 4. 初始化数据库

```bash
python init_db.py
```

这将创建 SQLite 数据库文件 `data/kimitalk.db` 并初始化表结构。

### 5. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

或使用启动脚本：

```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

## 🗄️ 数据库信息

### SQLite 配置

- **数据库类型**: SQLite
- **数据库文件**: `backend/data/kimitalk.db`
- **驱动**: aiosqlite (异步)
- **ORM**: SQLAlchemy 2.0

### 数据库表结构

#### conversations 表（对话表）

| 列名 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(36) | 主键，UUID |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### messages 表（消息表）

| 列名 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| conversation_id | VARCHAR(36) | 外键，关联对话 |
| role | VARCHAR(20) | 角色：user/assistant/system |
| content | TEXT | 消息内容 |
| timestamp | DATETIME | 消息时间 |

### 查看数据库

使用 SQLite 命令行工具：

```bash
# 安装 sqlite3（如果没有）
# Windows: 从 https://www.sqlite.org/download.html 下载
# Linux: sudo apt install sqlite3
# Mac: brew install sqlite3

# 打开数据库
cd backend/data
sqlite3 kimitalk.db

# SQLite 命令
.tables                      # 查看所有表
.schema conversations        # 查看表结构
SELECT * FROM conversations; # 查询对话
SELECT * FROM messages;      # 查询消息
.quit                        # 退出
```

## 🔧 常用 Conda 命令

### 环境管理

```bash
# 列出所有环境
conda env list

# 激活环境
conda activate kimitalk

# 退出环境
conda deactivate

# 删除环境
conda env remove -n kimitalk

# 更新环境
conda env update -f environment.yml
```

### 包管理

```bash
# 列出已安装的包
conda list

# 安装新包
conda install package_name
# 或
pip install package_name

# 更新包
conda update package_name
pip install --upgrade package_name

# 导出环境
conda env export > environment.yml
pip freeze > requirements.txt
```

## 📦 环境文件说明

### environment.yml

Conda 环境配置文件，包含：
- 环境名称
- Python 版本
- Conda 和 pip 依赖

### requirements.txt

纯 pip 依赖列表，用于：
- 非 Conda 环境
- Docker 容器
- 生产部署

两个文件保持同步，可以互换使用。

## 🐛 故障排查

### 问题 1: conda 命令找不到

**解决方法**:
```bash
# 检查 conda 是否安装
where conda  # Windows
which conda  # Linux/Mac

# 如果未安装，下载并安装 Miniconda
# https://docs.conda.io/en/latest/miniconda.html
```

### 问题 2: 环境创建失败

**解决方法**:
```bash
# 清理 conda 缓存
conda clean --all

# 重新创建环境
conda env create -f environment.yml --force
```

### 问题 3: 数据库初始化失败

**解决方法**:
```bash
# 检查 data 目录权限
# 删除旧数据库文件（如果存在）
rm -rf data/kimitalk.db

# 重新初始化
python init_db.py
```

### 问题 4: 包版本冲突

**解决方法**:
```bash
# 更新 conda
conda update conda

# 使用 pip 安装所有包
conda create -n kimitalk python=3.11
conda activate kimitalk
pip install -r requirements.txt
```

### 问题 5: aiosqlite 导入错误

**解决方法**:
```bash
# 确保激活了正确的环境
conda activate kimitalk

# 重新安装 aiosqlite
pip uninstall aiosqlite
pip install aiosqlite==0.19.0
```

## 🔄 数据库迁移（高级）

如果需要修改数据库结构，使用 Alembic：

### 初始化 Alembic

```bash
# 只需执行一次
alembic init alembic
```

### 创建迁移

```bash
# 修改 app/models/db_models.py 后
alembic revision --autogenerate -m "描述修改内容"
```

### 应用迁移

```bash
# 升级到最新版本
alembic upgrade head

# 降级一个版本
alembic downgrade -1
```

## 📊 性能优化

### SQLite 优化配置

在 `app/core/database.py` 中：

```python
# 启用 WAL 模式（提高并发性能）
async with engine.begin() as conn:
    await conn.execute(text("PRAGMA journal_mode=WAL"))
    await conn.execute(text("PRAGMA synchronous=NORMAL"))
```

### 索引优化

为常用查询添加索引：

```python
# 在 Message 模型中
__table_args__ = (
    Index('idx_conversation_timestamp', 'conversation_id', 'timestamp'),
)
```

## 📚 更多资源

- Conda 文档: https://docs.conda.io/
- SQLAlchemy 文档: https://docs.sqlalchemy.org/
- SQLite 文档: https://www.sqlite.org/docs.html
- FastAPI 数据库指南: https://fastapi.tiangolo.com/tutorial/sql-databases/

## ✅ 完成检查清单

- [ ] Conda 已安装
- [ ] kimitalk 环境已创建
- [ ] 环境已激活
- [ ] 所有依赖已安装
- [ ] 数据库已初始化
- [ ] 服务器可以正常启动
- [ ] API 文档可访问（http://localhost:8000/docs）
- [ ] 可以发送消息并收到回复

---

如有问题，请参考主项目文档或提交 Issue。
