"""数据库配置和连接"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings
import os

# 数据库文件路径
DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
os.makedirs(DATABASE_DIR, exist_ok=True)

DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(DATABASE_DIR, 'kimitalk.db')}"

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # 设为 True 可以看到 SQL 语句
    future=True
)

# 创建会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 声明基类
Base = declarative_base()


async def get_db() -> AsyncSession:
    """获取数据库会话（依赖注入）"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库（创建所有表）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
