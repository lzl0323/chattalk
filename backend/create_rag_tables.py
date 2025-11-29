"""
创建 RAG 相关数据库表
"""
import asyncio
from app.core.database import engine
from app.models.db_models import Base, KnowledgeBase, Document

async def create_tables():
    """创建表"""
    print("🔧 开始创建 RAG 数据库表...")
    
    # 导入所有模型以确保它们被注册到 Base.metadata
    from app.models import db_models
    
    async with engine.begin() as conn:
        # 使用 SQLAlchemy 自动创建所有表（如果不存在）
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ RAG 数据库表创建成功！")
    print("   - knowledge_bases (知识库表)")
    print("   - documents (文档表)")

if __name__ == "__main__":
    asyncio.run(create_tables())
