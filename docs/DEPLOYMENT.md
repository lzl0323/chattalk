# 部署指南

本文档详细说明如何在不同环境中部署 AI 对话系统。

## 目录

- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [Docker 部署（可选）](#docker-部署)
- [故障排查](#故障排查)

---

## 开发环境部署

开发环境无需 Nginx，前后端分别运行即可。

### 1. 后端部署

#### 1.1 环境准备

```bash
# 确保已安装 Python 3.9+
python --version

# 创建虚拟环境
cd backend
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### 1.2 安装依赖

```bash
pip install -r requirements.txt
```

#### 1.3 配置环境变量

```bash
# 复制环境变量模板
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# 编辑 .env 文件，填入你的 Kimi API 密钥
notepad .env  # 或使用其他编辑器
```

`.env` 文件内容示例：
```env
KIMI_API_KEY=sk-MLtlwyjKSv3kbe6jLyFndfCqsHtet4iImwE3M9TVH8p3AU15
KIMI_API_BASE=https://api.moonshot.cn/v1
KIMI_MODEL=moonshot-v1-8k
MAX_CONTEXT_MESSAGES=10
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### 1.4 启动后端服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或者直接运行
python -m app.main
```

服务将运行在 `http://localhost:8000`

查看 API 文档：`http://localhost:8000/docs`

### 2. 前端部署

#### 2.1 环境准备

```bash
# 确保已安装 Node.js 16+
node --version
npm --version

cd frontend
```

#### 2.2 安装依赖

```bash
npm install
```

如果安装速度慢，可以使用国内镜像：
```bash
npm install --registry=https://registry.npmmirror.com
```

#### 2.3 启动开发服务器

```bash
npm run dev
```

服务将运行在 `http://localhost:5173`

访问该地址即可使用应用。

### 3. 开发环境验证

1. 后端：访问 `http://localhost:8000/docs` 查看 API 文档
2. 前端：访问 `http://localhost:5173` 使用应用
3. 发送测试消息，确认流式响应正常工作

---

## 生产环境部署

生产环境使用 Gunicorn + Uvicorn 运行后端，Nginx 作为反向代理和静态文件服务器。

### 1. 后端生产部署

#### 1.1 安装生产依赖

```bash
cd backend
pip install gunicorn
```

#### 1.2 创建 Gunicorn 配置

创建 `backend/gunicorn.conf.py`:

```python
import multiprocessing

# 绑定地址
bind = "127.0.0.1:8000"

# Worker 进程数
workers = multiprocessing.cpu_count() * 2 + 1

# Worker 类型（必须使用 uvicorn workers）
worker_class = "uvicorn.workers.UvicornWorker"

# 超时时间
timeout = 300

# 日志
accesslog = "/var/log/ai_chat/access.log"
errorlog = "/var/log/ai_chat/error.log"
loglevel = "info"

# 进程名称
proc_name = "ai_chat_api"

# 后台运行
daemon = False
```

#### 1.3 创建日志目录

```bash
# Linux
sudo mkdir -p /var/log/ai_chat
sudo chown $USER:$USER /var/log/ai_chat

# Windows (PowerShell)
New-Item -ItemType Directory -Path C:\logs\ai_chat -Force
```

#### 1.4 启动生产服务

```bash
# 使用 Gunicorn 启动
gunicorn app.main:app -c gunicorn.conf.py

# 或者后台运行
gunicorn app.main:app -c gunicorn.conf.py --daemon
```

#### 1.5 配置系统服务（Linux）

创建 `/etc/systemd/system/ai-chat-api.service`:

```ini
[Unit]
Description=AI Chat API Service
After=network.target

[Service]
Type=notify
User=your-user
Group=your-group
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/backend/venv/bin"
ExecStart=/path/to/backend/venv/bin/gunicorn app.main:app -c gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start ai-chat-api
sudo systemctl enable ai-chat-api
sudo systemctl status ai-chat-api
```

### 2. 前端生产构建

#### 2.1 构建前端

```bash
cd frontend
npm run build
```

构建产物在 `frontend/dist` 目录。

#### 2.2 验证构建

```bash
# 预览构建结果
npm run preview
```

### 3. Nginx 配置

#### 3.1 复制配置文件

```bash
# Linux
sudo cp nginx/nginx.conf /etc/nginx/sites-available/ai-chat
sudo ln -s /etc/nginx/sites-available/ai-chat /etc/nginx/sites-enabled/

# Windows
# 将 nginx/nginx.conf 的内容添加到 nginx 安装目录的 conf/nginx.conf
```

#### 3.2 修改配置

编辑配置文件，修改以下内容：

1. **前端静态文件路径**：
   ```nginx
   root /path/to/your/frontend/dist;
   ```

2. **域名**（如果有）：
   ```nginx
   server_name your-domain.com;
   ```

3. **日志路径**（根据实际情况）：
   ```nginx
   access_log /var/log/nginx/ai_chat_access.log;
   error_log /var/log/nginx/ai_chat_error.log;
   ```

#### 3.3 测试配置

```bash
# Linux
sudo nginx -t

# Windows
nginx -t
```

#### 3.4 启动/重载 Nginx

```bash
# Linux
sudo systemctl start nginx
sudo systemctl reload nginx
sudo systemctl enable nginx

# Windows
nginx
# 或
nginx -s reload
```

### 4. HTTPS 配置（推荐）

#### 4.1 获取 SSL 证书

使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com
```

#### 4.2 更新 Nginx 配置

Certbot 会自动更新配置，或手动添加：

```nginx
listen 443 ssl http2;
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
```

#### 4.3 自动续期

```bash
# 测试续期
sudo certbot renew --dry-run

# 添加定时任务
sudo crontab -e
# 添加：0 0 * * * certbot renew --quiet
```

### 5. 生产环境验证

1. 访问你的域名或服务器 IP
2. 测试对话功能
3. 检查流式响应是否正常
4. 查看日志确认无错误

---

## Docker 部署（可选）

### 1. 创建 Dockerfile

**后端 Dockerfile** (`backend/Dockerfile`):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

**前端 Dockerfile** (`frontend/Dockerfile`):

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 2. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - KIMI_API_KEY=${KIMI_API_KEY}
      - KIMI_API_BASE=https://api.moonshot.cn/v1
      - KIMI_MODEL=moonshot-v1-8k
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### 3. 启动服务

```bash
# 创建 .env 文件设置环境变量
echo "KIMI_API_KEY=your-api-key" > .env

# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 故障排查

### 1. 后端问题

#### 问题：后端无法启动

**检查**：
```bash
# 查看日志
cat /var/log/ai_chat/error.log

# 检查端口占用
netstat -tlnp | grep 8000  # Linux
netstat -ano | findstr 8000  # Windows
```

**解决**：
- 确认依赖已安装：`pip list`
- 确认环境变量正确：检查 `.env` 文件
- 确认端口未被占用

#### 问题：Kimi API 调用失败

**检查**：
- API 密钥是否正确
- 网络是否可访问 `api.moonshot.cn`
- API 配额是否充足

```bash
# 测试 API 连接
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.moonshot.cn/v1/models
```

### 2. 前端问题

#### 问题：前端无法连接后端

**检查**：
- 浏览器控制台查看错误
- 检查 CORS 配置
- 确认后端服务正在运行

**解决**：
- 开发环境：确认 Vite 代理配置正确
- 生产环境：确认 Nginx 代理配置正确

#### 问题：流式响应不工作

**检查**：
- Nginx 是否禁用了缓冲：`proxy_buffering off;`
- 浏览器是否支持 SSE
- 网络是否稳定

### 3. Nginx 问题

#### 问题：502 Bad Gateway

**原因**：Nginx 无法连接到后端

**解决**：
```bash
# 检查后端服务状态
systemctl status ai-chat-api

# 检查后端是否在监听
netstat -tlnp | grep 8000

# 检查 Nginx 配置
sudo nginx -t
```

#### 问题：静态文件 404

**解决**：
- 确认 `root` 路径正确
- 确认文件权限：`chmod -R 755 /path/to/dist`
- 检查文件是否存在

### 4. 性能问题

#### 响应慢

**优化**：
- 增加 Gunicorn workers 数量
- 启用 Nginx 缓存
- 使用 CDN 加速静态资源
- 优化数据库查询（如果使用）

#### 内存占用高

**优化**：
- 减少 workers 数量
- 定期清理过期对话
- 使用 Redis 存储会话而非内存

### 5. 日志查看

```bash
# 后端日志
tail -f /var/log/ai_chat/error.log

# Nginx 日志
tail -f /var/log/nginx/ai_chat_error.log

# 系统服务日志
journalctl -u ai-chat-api -f
```

---

## 安全建议

1. **HTTPS**: 生产环境必须使用 HTTPS
2. **防火墙**: 只开放必要端口（80, 443）
3. **API 密钥**: 使用环境变量，不要提交到代码库
4. **速率限制**: 使用 Nginx 限制请求频率
5. **日志审计**: 定期检查访问日志
6. **更新**: 定期更新依赖和系统补丁

---

## 监控和维护

### 1. 健康检查

```bash
# API 健康检查
curl http://localhost:8000/api/health

# 前端检查
curl http://localhost/
```

### 2. 定期维护

- 清理日志文件
- 备份配置文件
- 更新依赖包
- 监控磁盘空间

### 3. 监控工具（推荐）

- **应用监控**: Prometheus + Grafana
- **日志聚合**: ELK Stack (Elasticsearch + Logstash + Kibana)
- **APM**: New Relic, Datadog
- **错误追踪**: Sentry

---

## 扩展部署

### 多服务器部署

使用 Nginx 负载均衡：

```nginx
upstream fastapi_backend {
    server 192.168.1.10:8000 weight=3;
    server 192.168.1.11:8000 weight=2;
    server 192.168.1.12:8000 backup;
}
```

### 使用 Redis

替换内存存储为 Redis：

```python
# backend/app/services/redis_store.py
import redis

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)
```

---

如有问题，请参考项目 README 或提交 Issue。
