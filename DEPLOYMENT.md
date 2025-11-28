# 🚀 ChatTalk 部署指南

## 快速部署（免费方案）

### 方案 1：Vercel + Railway（推荐）⭐

这是最简单的部署方式，完全免费，而且自动化部署。

#### 步骤 1：部署前端到 Vercel

1. **注册 Vercel**
   - 访问：https://vercel.com
   - 点击右上角 "Sign Up"
   - 选择 "Continue with GitHub"

2. **导入项目**
   - 登录后点击 "Add New..." → "Project"
   - 选择你的 `chattalk` 仓库
   - 点击 "Import"

3. **配置项目**
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

4. **添加环境变量**
   - 点击 "Environment Variables"
   - 添加：
     ```
     VITE_API_BASE_URL = 你的后端地址（稍后从 Railway 获取）
     ```

5. **部署**
   - 点击 "Deploy"
   - 等待 2-3 分钟，完成！
   - 你会得到一个域名，如：`chattalk.vercel.app`

#### 步骤 2：部署后端到 Railway

1. **注册 Railway**
   - 访问：https://railway.app
   - 点击 "Login with GitHub"

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择 `chattalk` 仓库

3. **配置服务**
   - Railway 会自动检测 Python 项目
   - 点击项目 → Settings → 配置：
     ```
     Root Directory: backend
     Start Command: python -m app.core.init_db && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

4. **添加环境变量**
   - 点击 "Variables" 标签
   - 添加以下变量：
     ```
     DATABASE_URL=sqlite:///./chattalk.db
     SECRET_KEY=你的随机密钥（至少32位）
     ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=10080
     
     # CORS 配置（填入你的 Vercel 域名）
     CORS_ORIGINS=https://你的vercel域名.vercel.app
     
     # OCR 配置
     OCR_API_BASE=https://api.siliconflow.cn/v1
     OCR_API_KEY=你的OCR密钥
     OCR_MODEL=Pro/Qwen/Qwen2-VL-7B-Instruct
     ```

5. **生成域名**
   - 点击 "Settings" → "Networking"
   - 点击 "Generate Domain"
   - 你会得到一个域名，如：`chattalk-production.up.railway.app`

6. **更新前端环境变量**
   - 回到 Vercel 项目
   - Settings → Environment Variables
   - 更新 `VITE_API_BASE_URL` 为 Railway 域名
   - 重新部署

#### 完成！🎉

现在你的网站已经在线了！
- 前端：`https://你的项目.vercel.app`
- 后端：`https://你的项目.up.railway.app`

---

### 方案 2：Zeabur（中文界面，一站式）⭐

#### 优点
- 中文界面，更容易理解
- 前后端一起部署
- 国内访问速度快

#### 部署步骤

1. **注册**
   - 访问：https://zeabur.com/zh-CN
   - 点击 "开始使用"
   - 用 GitHub 登录

2. **创建项目**
   - 点击 "新建项目"
   - 选择 "从 GitHub 导入"
   - 选择 `chattalk` 仓库

3. **配置服务**
   - Zeabur 会自动识别前后端
   - 后端服务：
     - 根目录：`backend`
     - 构建命令：自动
     - 启动命令：`python -m app.core.init_db && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   
   - 前端服务：
     - 根目录：`frontend`
     - 构建命令：`npm run build`
     - 输出目录：`dist`

4. **添加环境变量**
   - 在后端服务中添加：
     ```
     DATABASE_URL=sqlite:///./chattalk.db
     SECRET_KEY=你的密钥
     OCR_API_KEY=你的OCR密钥
     CORS_ORIGINS=https://你的前端域名.zeabur.app
     ```

5. **绑定域名**
   - 每个服务都会自动分配域名
   - 或者绑定你自己的域名

6. **部署**
   - 点击 "部署" 按钮
   - 等待几分钟，完成！

---

### 方案 3：Render（全栈部署）

#### 优点
- 免费 PostgreSQL 数据库
- 前后端都支持
- 稳定可靠

#### 部署步骤

1. **注册 Render**
   - 访问：https://render.com
   - 用 GitHub 登录

2. **部署后端**
   - 点击 "New +" → "Web Service"
   - 连接 GitHub 仓库
   - 配置：
     ```
     Name: chattalk-backend
     Root Directory: backend
     Build Command: pip install -r requirements.txt
     Start Command: python -m app.core.init_db && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - 添加环境变量（同上）

3. **部署前端**
   - 点击 "New +" → "Static Site"
   - 选择同一个仓库
   - 配置：
     ```
     Name: chattalk-frontend
     Root Directory: frontend
     Build Command: npm run build
     Publish Directory: dist
     ```

4. **配置 CORS**
   - 在后端环境变量中添加前端域名

---

## 📋 部署前检查清单

- [ ] 已将代码推送到 GitHub
- [ ] 有可用的 API Key（OpenAI、OCR 等）
- [ ] 已生成强密钥（可用 `openssl rand -hex 32`）
- [ ] 前端 API 地址配置正确
- [ ] CORS 配置包含前端域名

---

## 🔧 常见问题

### Q: 部署后 500 错误？
A: 检查环境变量是否都配置正确，特别是 `SECRET_KEY` 和数据库配置。

### Q: 前端无法连接后端？
A: 检查 CORS 配置，确保后端 `CORS_ORIGINS` 包含前端域名。

### Q: 数据库迁移失败？
A: 在启动命令中添加 `python -m app.core.init_db &&` 确保数据库初始化。

### Q: 文件上传失败？
A: 免费服务器通常不支持持久化文件存储，建议使用对象存储（如 S3、阿里云 OSS）。

### Q: 免费套餐够用吗？
A: 对于个人项目和小规模使用完全够用。如果流量大了可以升级付费套餐。

---

## 💡 进阶优化

### 使用自定义域名
大多数平台都支持绑定自己的域名：
1. 在域名注册商添加 CNAME 记录
2. 在平台设置中绑定域名
3. 等待 DNS 生效（通常几分钟）

### 使用 PostgreSQL
Railway 和 Render 提供免费 PostgreSQL：
1. 在平台添加 PostgreSQL 服务
2. 自动获得 `DATABASE_URL`
3. 更新后端环境变量

### 启用 HTTPS
所有推荐的平台都自动提供免费 HTTPS 证书，无需配置。

### 自动部署
连接 GitHub 后，每次推送代码都会自动部署，无需手动操作。

---

## 📞 需要帮助？

如果遇到问题：
1. 查看平台的日志输出
2. 检查环境变量配置
3. 确认代码已推送到 GitHub
4. 查看平台官方文档

---

**祝部署顺利！🚀**
