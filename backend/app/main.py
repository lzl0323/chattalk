"""FastAPI 主应用"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .core.config import settings
from .core.database import init_db, close_db
from .api.chat import router as chat_router
from .api.auth import router as auth_router
from .api.conversations import router as conversations_router
from .api.model_configs import router as model_configs_router
from .api.suggestions import router as suggestions_router
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 注册路由
app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(model_configs_router)
app.include_router(suggestions_router)
app.include_router(chat_router)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
