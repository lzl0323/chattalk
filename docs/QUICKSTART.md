# 快速开始指南

10 分钟内启动你的 AI 对话系统！

## 前置要求

- **Python**: 3.9 或更高版本
- **Node.js**: 16 或更高版本
- **Kimi API 密钥**: sk-MLtlwyjKSv3kbe6jLyFndfCqsHtet4iImwE3M9TVH8p3AU15

## 步骤 1: 克隆/下载项目

项目已经在 `E:\PROJECT-lzl\vue+fastapi`

## 步骤 2: 启动后端 (2 分钟)

### Windows PowerShell

```powershell
# 进入后端目录
cd E:\PROJECT-lzl\vue+fastapi\backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 环境变量已配置在 .env 文件中

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Windows CMD

```cmd
cd E:\PROJECT-lzl\vue+fastapi\backend
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**成功标志**: 看到 `Application startup complete` 并且可以访问 http://localhost:8000/docs

## 步骤 3: 启动前端 (2 分钟)

**打开新的终端窗口**

### PowerShell / CMD

```powershell
# 进入前端目录
cd E:\PROJECT-lzl\vue+fastapi\frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

**成功标志**: 看到 `Local: http://localhost:5173/`

## 步骤 4: 开始使用

1. 打开浏览器访问: **http://localhost:5173**
2. 在输入框输入你的问题
3. 按 Enter 发送
4. 观察 AI 实时回复！

---

## 验证安装

### 检查后端

访问 API 文档: http://localhost:8000/docs

健康检查: http://localhost:8000/api/health

### 检查前端

访问应用: http://localhost:5173

应该看到欢迎界面和示例问题。

---

## 常见问题

### Q: 后端启动失败 - "No module named 'xxx'"

**A**: 确保在虚拟环境中并已安装依赖
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Q: 前端启动失败 - "Cannot find module"

**A**: 重新安装依赖
```powershell
rm -r node_modules
npm install
```

### Q: API 调用失败 - "API key error"

**A**: 检查 `backend/.env` 文件中的 `KIMI_API_KEY` 是否正确

### Q: 流式响应不工作

**A**: 
1. 确保后端运行正常
2. 检查浏览器控制台是否有错误
3. 确认 CORS 配置正确

### Q: 端口被占用

**A**: 修改端口号
```powershell
# 后端使用其他端口
uvicorn app.main:app --reload --port 8001

# 前端 - 编辑 vite.config.js 修改 port
```

---

## 下一步

- 📖 阅读 [详细设计文档](docs/DESIGN.md)
- 🚀 查看 [部署指南](docs/DEPLOYMENT.md)
- 💡 了解 [流式处理](docs/STREAM_NOTES.md)
- ⚙️ 自定义 [System Prompt](backend/app/core/prompts.py)

---

## 停止服务

### 停止后端
在后端终端按 `Ctrl + C`

### 停止前端
在前端终端按 `Ctrl + C`

---

## 完整命令速查

### 后端
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### 前端
```powershell
cd frontend
npm run dev
```

---

祝你使用愉快！如有问题，请查阅文档或提交 Issue。
