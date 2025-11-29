"""FastAPI 主应用"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os

from .core.config import settings
from .core.database import init_db, close_db
from .api.chat import router as chat_router
from .api.auth import router as auth_router
from .api.conversations import router as conversations_router
from .api.model_configs import router as model_configs_router
from .api.suggestions import router as suggestions_router
from .api.ocr import router as ocr_router
from .api.rag import router as rag_router
from .services.kimi import kimi_service

# 配置日志
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info("Starting AI Chat Application...")
    logger.info(f"Kimi API Base: {settings.kimi_api_base}")
    logger.info(f"Kimi Model: {settings.kimi_model}")
    logger.info(f"CORS Origins: {settings.cors_origins_list}")
    
    # 初始化数据库
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # 关闭
    logger.info("Shutting down AI Chat Application...")
    await kimi_service.close()
    await close_db()
    logger.info("Database connections closed")


# 创建 FastAPI 应用
app = FastAPI(
    title="AI 对话系统 API",
    description="基于 FastAPI 的 AI 对话系统后端，支持流式响应",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
# 开发环境：使用正则匹配局域网IP + localhost，生产环境使用配置的源
is_dev = settings.log_level in ["DEBUG", "INFO"]

if is_dev:
    # 允许localhost和所有局域网IP（192.168.x.x, 10.x.x.x, 172.16-31.x.x）
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
    logger.info("CORS configured: Development mode - allowing all local/LAN origins with credentials")
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
    logger.info(f"CORS configured: Production mode - {settings.cors_origins_list}")

# 首先定义普通路由
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "AI 对话系统 API",
        "version": "1.0.0",
        "status": "running",
        "database": "sqlite",
        "docs": "/docs",
        "health": "/api/health"
    }

# 注册 API 路由
app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(model_configs_router)
app.include_router(suggestions_router)
app.include_router(ocr_router)
app.include_router(rag_router)
app.include_router(chat_router)

# 最后挂载静态文件服务（必须在所有路由之后）
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
    logger.info(f"Created uploads directory: {UPLOAD_DIR}")

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
logger.info(f"Static files mounted at /uploads -> {UPLOAD_DIR}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
