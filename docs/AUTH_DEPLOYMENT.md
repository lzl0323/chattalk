# 用户认证与聊天历史功能 - 部署指南

本文档详细说明了如何部署带有用户认证和聊天历史功能的 AI 对话系统。

## 📋 目录

1. [系统要求](#系统要求)
2. [后端部署](#后端部署)
3. [前端部署](#前端部署)
4. [Nginx 配置](#nginx-配置)
5. [环境变量配置](#环境变量配置)
6. [数据库迁移](#数据库迁移)
7. [生产环境优化](#生产环境优化)
8. [故障排查](#故障排查)

---

## 系统要求

### 后端
- Python 3.11+
- SQLite 3
- 8GB+ RAM（推荐）

### 前端
- Node.js 18+
- npm 9+

### 服务器
- Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- Nginx 1.18+
- 20GB+ 磁盘空间

---

## 后端部署

### 1. 安装依赖

```bash
cd backend

# 使用 Conda（推荐）
conda env create -f environment.yml
conda activate kimitalk

# 或使用 venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
cd backend
cp .env.example .env
```

编辑 `.env`：

```env
# Kimi API 配置
KIMI_API_KEY=你的API密钥
KIMI_API_BASE=https://api.moonshot.cn/v1
KIMI_MODEL=moonshot-v1-8k

# JWT 认证配置（生产环境必须修改）
JWT_SECRET_KEY=your-very-secure-secret-key-at-least-32-characters-long-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7天

# 应用配置
MAX_CONTEXT_MESSAGES=10
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173,http://yourdomain.com

# 速率限制
MAX_REQUESTS_PER_MINUTE=60
```

⚠️ **安全提示**：
- `JWT_SECRET_KEY` 必须使用强随机字符串（至少 32 字符）
- 生产环境不要使用示例密钥
- 可以使用以下命令生成安全密钥：
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

### 3. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head

# 验证数据库
sqlite3 data/kimitalk.db
.tables  # 应该看到 users, conversations, messages 表
.quit
```

### 4. 启动后端服务

#### 开发环境

```bash
# 使用 start.bat（Windows）
start.bat

# 或使用 start.sh（Linux/Mac）
chmod +x start.sh
./start.sh

# 或直接使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 生产环境

使用 Gunicorn + Uvicorn workers：

```bash
# 安装 gunicorn
pip install gunicorn

# 启动服务（4 个 worker）
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --daemon
```

创建 systemd 服务（Linux）：

```bash
sudo nano /etc/systemd/system/chattalk-api.service
```

```ini
[Unit]
Description=ChaTalk FastAPI Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/chattalk/backend
Environment="PATH=/path/to/chattalk/backend/venv/bin"
ExecStart=/path/to/chattalk/backend/venv/bin/gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info
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
sudo systemctl enable chattalk-api
sudo systemctl start chattalk-api
sudo systemctl status chattalk-api
```

---

## 前端部署

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

### 3. 配置

如果 API 地址不是默认的，修改 `vite.config.js`：

```javascript
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // 修改为你的 API 地址
        changeOrigin: true
      }
    }
  }
})
```

---

## Nginx 配置

### 完整配置示例

```nginx
# /etc/nginx/sites-available/chattalk

server {
    listen 80;
    server_name yourdomain.com;

    # 前端静态文件
    root /path/to/chattalk/frontend/dist;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # 前端路由（SPA）
    location / {
        try_files $uri $uri/ /index.html;
        
        # 缓存策略
        add_header Cache-Control "no-cache";
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        
        # 代理头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE 流式支持（关键！）
        proxy_buffering off;
        proxy_cache off;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        chunked_transfer_encoding off;
        
        # 超时设置
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 限制请求大小
    client_max_body_size 10M;
}
```

### HTTPS 配置（使用 Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书并自动配置
sudo certbot --nginx -d yourdomain.com

# 测试自动续期
sudo certbot renew --dry-run
```

HTTPS 配置会自动添加，或手动添加：

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... 其他配置同上
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/chattalk /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

---

## 环境变量配置

### 后端环境变量说明

| 变量 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `KIMI_API_KEY` | ✅ | - | Kimi API 密钥 |
| `KIMI_API_BASE` | ❌ | `https://api.moonshot.cn/v1` | API 基础 URL |
| `KIMI_MODEL` | ❌ | `moonshot-v1-8k` | 使用的模型 |
| `JWT_SECRET_KEY` | ✅ | - | JWT 签名密钥（必须修改！） |
| `JWT_ALGORITHM` | ❌ | `HS256` | JWT 算法 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | `10080` | Token 过期时间（分钟） |
| `MAX_CONTEXT_MESSAGES` | ❌ | `10` | 最大上下文消息数 |
| `LOG_LEVEL` | ❌ | `INFO` | 日志级别 |
| `CORS_ORIGINS` | ❌ | `http://localhost:5173` | 允许的跨域源 |

---

## 数据库迁移

### 初次部署

```bash
cd backend
alembic upgrade head
```

### 更新数据库结构

```bash
# 备份数据库
cp data/kimitalk.db data/kimitalk.db.backup

# 运行迁移
alembic upgrade head

# 如果出错，回滚
alembic downgrade -1
```

详细迁移文档：[DATABASE_MIGRATION.md](../backend/DATABASE_MIGRATION.md)

---

## 生产环境优化

### 1. 性能优化

```python
# app/core/config.py
class Settings(BaseSettings):
    # 连接池大小
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # 缓存设置
    cache_ttl: int = 3600
```

### 2. 日志配置

```python
# 生产环境日志
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
logging.basicConfig(handlers=[handler])
```

### 3. 监控

#### 健康检查端点

```bash
curl http://localhost:8000/api/health
```

#### 使用 Supervisor 管理进程

```bash
sudo apt install supervisor
sudo nano /etc/supervisor/conf.d/chattalk.conf
```

```ini
[program:chattalk-api]
command=/path/to/venv/bin/gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
directory=/path/to/chattalk/backend
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/chattalk/err.log
stdout_logfile=/var/log/chattalk/out.log
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start chattalk-api
```

### 4. 备份策略

```bash
# 每日备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/chattalk"
DB_FILE="/path/to/chattalk/backend/data/kimitalk.db"

mkdir -p $BACKUP_DIR
cp $DB_FILE $BACKUP_DIR/kimitalk_$DATE.db

# 保留最近 7 天的备份
find $BACKUP_DIR -name "kimitalk_*.db" -mtime +7 -delete
```

添加到 crontab：

```bash
0 2 * * * /path/to/backup.sh
```

---

## 故障排查

### 问题 1：认证失败

**症状**：登录后立即被踢出

**解决**：
1. 检查 JWT_SECRET_KEY 是否配置
2. 检查 token 是否正确保存在 localStorage
3. 查看浏览器控制台错误

### 问题 2：跨域错误

**症状**：前端无法访问 API

**解决**：
1. 检查 `CORS_ORIGINS` 环境变量
2. 确保包含前端域名
3. Nginx 配置中添加 CORS 头（如果需要）

### 问题 3：流式响应中断

**症状**：AI 回复不完整

**解决**：
1. Nginx 配置中禁用缓冲：`proxy_buffering off`
2. 增加超时时间：`proxy_read_timeout 300s`
3. 检查网络稳定性

### 问题 4：数据库锁定

**症状**：写入失败，`database is locked`

**解决**：
```python
# SQLite 配置
DATABASE_URL = "sqlite+aiosqlite:///./data/kimitalk.db?check_same_thread=False"
```

### 查看日志

```bash
# 后端日志
tail -f logs/app.log

# Nginx 日志
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Systemd 日志
sudo journalctl -u chattalk-api -f
```

---

## 快速部署脚本

### 一键部署脚本（Ubuntu）

```bash
#!/bin/bash

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}开始部署 ChaTalk...${NC}"

# 1. 后端
echo "部署后端..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# 2. 前端
echo "构建前端..."
cd ../frontend
npm install
npm run build

# 3. Nginx
echo "配置 Nginx..."
sudo cp nginx/nginx.conf /etc/nginx/sites-available/chattalk
sudo ln -sf /etc/nginx/sites-available/chattalk /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

echo -e "${GREEN}部署完成！${NC}"
echo "请访问: http://$(hostname -I | awk '{print $1}')"
```

---

## 总结

部署完成后，你应该能够：

✅ 用户可以注册和登录  
✅ 聊天消息自动保存到数据库  
✅ 侧边栏显示历史对话  
✅ 支持对话搜索和管理  
✅ JWT Token 自动刷新  
✅ 流式响应正常工作

如有问题，请参考[故障排查](#故障排查)部分或查看详细日志。
