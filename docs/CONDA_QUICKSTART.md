# Conda + SQLite 快速启动指南

## 🎯 一键设置（推荐）

### Windows

```cmd
cd E:\PROJECT-lzl\vue+fastapi\backend
setup_conda.bat
```

**完成后**：
```cmd
conda activate kimitalk
start.bat
```

### Linux/Mac

```bash
cd /path/to/vue+fastapi/backend
chmod +x setup_conda.sh
./setup_conda.sh

# 完成后
conda activate kimitalk
./start.sh
```

---

## 📋 手动步骤（如果需要）

### 1. 创建 Conda 环境

```bash
cd backend
conda env create -f environment.yml
```

### 2. 激活环境

```bash
conda activate kimitalk
```

### 3. 验证安装

```bash
python --version
# 应显示: Python 3.11.x

pip list | findstr sqlalchemy
# 应看到 SQLAlchemy
```

### 4. 初始化数据库（自动）

数据库会在首次启动时自动初始化，或手动运行：

```bash
python init_db.py
```

### 5. 启动后端

```bash
# 方式 1: 使用启动脚本（推荐）
start.bat          # Windows
./start.sh         # Linux/Mac

# 方式 2: 直接运行
uvicorn app.main:app --reload
```

### 6. 启动前端（新终端）

```bash
cd ../frontend
npm install        # 首次运行
npm run dev
```

---

## 🗄️ 数据库信息

- **类型**: SQLite
- **位置**: `backend/data/kimitalk.db`
- **自动创建**: ✅ 首次启动时
- **持久化**: ✅ 数据保存在文件中

### 查看数据

```bash
cd backend/data
sqlite3 kimitalk.db

# SQLite 命令
.tables                          # 查看所有表
SELECT COUNT(*) FROM messages;   # 消息数量
SELECT * FROM conversations 
  ORDER BY updated_at DESC 
  LIMIT 5;                       # 最近 5 个对话
.quit                            # 退出
```

---

## 🔄 切换环境

### 从虚拟环境切换到 Conda

如果之前使用 venv：

```bash
# 退出 venv
deactivate

# 删除 venv（可选）
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

# 激活 Conda 环境
conda activate kimitalk
```

### 从 Conda 切换回虚拟环境

```bash
# 退出 Conda
conda deactivate

# 使用 venv
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

---

## 🆚 环境对比

| 特性 | Conda (kimitalk) | venv + pip |
|------|------------------|------------|
| 环境隔离 | ✅ 优秀 | ✅ 良好 |
| 包管理 | Conda + pip | 仅 pip |
| 系统库 | ✅ 可管理 | ❌ 依赖系统 |
| 跨平台 | ✅ 一致 | 部分差异 |
| 科学计算 | ✅ 优化 | 需手动配置 |
| 速度 | 较慢 | 较快 |
| 磁盘占用 | 较大 | 较小 |

**推荐**：
- **开发/数据分析**: 使用 Conda
- **生产部署/Docker**: 使用 venv + pip

---

## 📦 包管理

### 安装新包

```bash
# 方式 1: Conda（推荐）
conda install package_name

# 方式 2: pip
pip install package_name

# 更新 environment.yml
conda env export > environment.yml

# 更新 requirements.txt
pip freeze > requirements.txt
```

### 更新所有包

```bash
# Conda 包
conda update --all

# pip 包
pip list --outdated
pip install --upgrade package_name
```

---

## ✅ 验证清单

运行以下命令验证设置：

```bash
# 1. 检查 Python 版本
python --version
# 预期: Python 3.11.x

# 2. 检查 Conda 环境
conda env list
# 预期: 看到 kimitalk (激活状态有 *)

# 3. 检查关键包
python -c "import fastapi; print(fastapi.__version__)"
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
python -c "import aiosqlite; print(aiosqlite.__version__)"

# 4. 检查数据库
ls backend/data/kimitalk.db  # Linux/Mac
dir backend\data\kimitalk.db  # Windows
# 预期: 文件存在

# 5. 测试 API
curl http://localhost:8000/api/health
# 预期: {"status":"healthy",...}
```

---

## 🐛 常见问题

### Q: conda 命令未找到

**A**: 
1. 确认已安装 Anaconda 或 Miniconda
2. 重新打开终端
3. Windows: 检查环境变量 PATH

### Q: 环境创建失败

**A**:
```bash
# 清理缓存
conda clean --all

# 强制重新创建
conda env remove -n kimitalk
conda env create -f environment.yml
```

### Q: 数据库文件在哪里？

**A**: 
- 位置: `backend/data/kimitalk.db`
- 首次启动时自动创建
- 可以手动运行 `python init_db.py`

### Q: 如何重置数据库？

**A**:
```bash
# 停止服务器
# Ctrl+C

# 删除数据库
rm backend/data/kimitalk.db  # Linux/Mac
del backend\data\kimitalk.db  # Windows

# 重新初始化
python init_db.py

# 重启服务器
start.bat  # Windows
./start.sh  # Linux/Mac
```

### Q: 内存存储 vs 数据库有什么区别？

**A**:

| 特性 | 内存存储（旧版） | SQLite 数据库（新版） |
|------|------------------|----------------------|
| 数据持久化 | ❌ 重启丢失 | ✅ 永久保存 |
| 并发支持 | ⚠️ 有限 | ✅ 更好 |
| 查询能力 | ❌ 基本 | ✅ 强大 SQL |
| 适合场景 | 测试/演示 | 生产环境 |

---

## 🚀 下一步

1. ✅ **环境已设置**: Conda kimitalk 环境
2. ✅ **数据库已配置**: SQLite 自动初始化
3. ✅ **服务器运行中**: http://localhost:8000
4. ✅ **前端运行中**: http://localhost:5173

**现在可以**:
- 🎨 自定义 UI 样式
- 💬 修改 System Prompt
- 🗄️ 查看数据库中的对话记录
- 📊 添加更多功能（如用户认证）

---

## 📚 相关文档

- `backend/CONDA_SETUP.md` - Conda 详细设置指南
- `docs/DEPLOYMENT.md` - 生产环境部署
- `README.md` - 项目总览
- `QUICKSTART.md` - 原始快速开始（venv 版本）

---

**享受你的 AI 对话系统吧！** 🎉
