# 🚀 Render 免费部署完整指南

## 为什么选择 Render？

- ✅ **完全免费** - 不需要信用卡
- ✅ **稳定可靠** - 大公司背书，很多开源项目在用
- ✅ **自动 HTTPS** - 免费 SSL 证书
- ✅ **自动部署** - GitHub 推送自动更新
- ✅ **免费数据库** - PostgreSQL 数据库（可选）

## 部署步骤

### 第一步：注册 Render

1. 访问 https://render.com
2. 点击右上角 "Get Started"
3. 选择 "Sign in with GitHub"
4. 授权 Render 访问你的 GitHub

### 第二步：部署后端

#### 1. 创建 Web Service

- 登录后点击右上角 "New +" 按钮
- 选择 "Web Service"
- 点击 "Connect account" 连接 GitHub（如果还没连接）

#### 2. 选择仓库

- 在列表中找到 `chattalk` 仓库
- 点击右侧的 "Connect" 按钮

#### 3. 配置服务

**基础设置：**
```
Name: chattalk-backend
Region: Singapore (新加坡，离中国最近)
Branch: main
Root Directory: backend
```

**环境设置：**
```
Runtime: Python 3
```

**构建设置：**
```
Build Command: pip install -r requirements.txt
```

**启动设置：**
```
Start Command: python -m app.core.init_db && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### 4. 选择免费套餐

- **Instance Type: Free**
- 免费套餐包括：
  - 750 小时/月运行时间
  - 512 MB RAM
  - 自动休眠（15 分钟无请求）

#### 5. 添加环境变量

点击 "Advanced" 展开高级选项，添加以下环境变量：

| Key | Value |
|-----|-------|
| `SECRET_KEY` | 你的32位随机密钥 |
| `DATABASE_URL` | `sqlite:///./chattalk.db` |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` |
| `OCR_API_BASE` | `https://api.siliconflow.cn/v1` |
| `OCR_API_KEY` | 你的 SiliconFlow API Key |
| `OCR_MODEL` | `Pro/Qwen/Qwen2-VL-7B-Instruct` |
| `CORS_ORIGINS` | 先留空，等前端部署后填 |

**生成 SECRET_KEY：**
在本地运行以下命令生成：
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
或者访问：https://generate-secret.vercel.app/32

#### 6. 创建服务

- 点击底部的 "Create Web Service" 按钮
- 等待 5-10 分钟，Render 会自动构建和部署
- 部署成功后，会显示你的后端地址

**你的后端地址：**
```
https://chattalk-backend.onrender.com
```

**测试后端是否正常：**
访问：`https://chattalk-backend.onrender.com/docs`
应该能看到 Swagger API 文档。

---

### 第三步：部署前端到 Vercel

#### 1. 访问 Vercel

- 打开 https://vercel.com
- 用 GitHub 登录

#### 2. 导入项目

- 点击 "Add New..." → "Project"
- 选择 `chattalk` 仓库
- 点击 "Import"

#### 3. 配置项目

```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

#### 4. 添加环境变量

点击 "Environment Variables"，添加：

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://chattalk-backend.onrender.com` |

（填入你的 Render 后端地址）

#### 5. 部署

- 点击 "Deploy" 按钮
- 等待 2-3 分钟
- 部署成功！

**你的前端地址：**
```
https://chattalk.vercel.app
```

---

### 第四步：更新 CORS 配置

现在需要让后端允许前端访问：

1. **回到 Render**
   - 打开你的后端服务
   - 点击左侧 "Environment" 菜单

2. **更新 CORS_ORIGINS**
   - 找到 `CORS_ORIGINS` 变量
   - 修改为你的 Vercel 前端地址：
     ```
     https://chattalk.vercel.app
     ```
   - 点击 "Save Changes"

3. **服务会自动重启**
   - 等待 1-2 分钟

---

## ✅ 部署完成！

现在你可以访问你的网站了：

**前端访问地址：** https://chattalk.vercel.app

---

## 🔧 常见问题

### Q1: 后端首次访问很慢？

**原因：** 免费套餐会在 15 分钟无请求后自动休眠。

**解决方案：**
- 第一次访问会唤醒服务，需要等待 30-50 秒
- 可以使用 cron-job.org 等服务定时 ping 你的后端保持活跃
- 或者升级到付费套餐（$7/月）

### Q2: 数据库数据会丢失吗？

**SQLite 的限制：**
- ⚠️ Render 的免费套餐使用临时存储
- ⚠️ 服务重启后数据可能丢失

**推荐方案：升级到 PostgreSQL**

1. 在 Render 项目页面点击 "New +" → "PostgreSQL"
2. 选择 Free 套餐
3. 创建后会自动生成 `DATABASE_URL`
4. 复制 `DATABASE_URL` 到后端环境变量
5. 修改后端代码以支持 PostgreSQL（如果还没支持）

### Q3: 文件上传会丢失吗？

**是的。** 免费套餐不支持持久化文件存储。

**解决方案：**
- 使用对象存储服务（如 AWS S3、阿里云 OSS、Cloudinary）
- Cloudinary 提供免费额度，适合图片存储

### Q4: 如何查看日志？

1. 打开 Render Dashboard
2. 点击你的服务
3. 点击左侧 "Logs" 菜单
4. 实时查看日志输出

### Q5: 如何绑定自己的域名？

1. 在 Render 服务页面点击 "Settings"
2. 找到 "Custom Domain" 部分
3. 添加你的域名
4. 在域名注册商添加 CNAME 记录
5. 等待 DNS 生效

---

## 📊 监控和维护

### 保持服务活跃

使用 cron-job.org 设置定时任务：

1. 访问 https://cron-job.org
2. 注册账号
3. 创建新的 Cron Job：
   - URL: `https://chattalk-backend.onrender.com/docs`
   - 执行频率: 每 14 分钟
4. 这样可以防止服务休眠

### 查看服务状态

在 Render Dashboard 可以看到：
- CPU 使用率
- 内存使用
- 请求数量
- 响应时间

---

## 🚀 升级选项

如果免费套餐不够用，可以考虑升级：

**Render Starter ($7/月)：**
- 不会休眠
- 持久化存储
- 更好的性能

**PostgreSQL ($7/月)：**
- 1GB 数据库存储
- 数据持久化
- 自动备份

---

## 📝 自动部署

Render 已经自动配置了 CI/CD：

- ✅ 每次 `git push` 到 GitHub
- ✅ Render 自动检测变化
- ✅ 自动构建和部署
- ✅ 零停机更新

---

**遇到问题？查看 Render 日志或告诉我！** 🚀
