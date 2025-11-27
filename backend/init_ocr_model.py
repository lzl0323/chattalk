"""
初始化 DeepSeek OCR 模型配置
运行此脚本添加 OCR 模型到数据库
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker
from app.models.db_models import ModelConfig
from app.core.encryption import encrypt_api_key

async def init_ocr_model():
    """添加 DeepSeek OCR 模型配置"""
    
    # OCR 模型配置
    api_key = "sk-ayghpphczpwrrstumeodmfxefwnxfokudjmwqspvskjaapep"
    
    async with async_session_maker() as db:
        # 检查是否已存在
        from sqlalchemy import select
        result = await db.execute(
            select(ModelConfig).where(ModelConfig.name == "DeepSeek OCR")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("✅ DeepSeek OCR 模型已存在，更新配置...")
            existing.model = "deepseek-ai/DeepSeek-OCR"
            existing.model_type = "ocr"
            existing.api_base = "https://api.siliconflow.cn/v1"
            existing.api_key_encrypted = encrypt_api_key(api_key)
            existing.quota_limit = 1000000.0
            existing.quota_used = 0.0
            existing.is_active = True
            existing.description = "SiliconFlow DeepSeek OCR - 支持图片和PDF文档识别"
        else:
            print("📦 添加新的 DeepSeek OCR 模型配置...")
            ocr_model = ModelConfig(
                name="DeepSeek OCR",
                model="deepseek-ai/DeepSeek-OCR",
                model_type="ocr",
                api_base="https://api.siliconflow.cn/v1",
                api_key_encrypted=encrypt_api_key(api_key),
                quota_limit=1000000.0,
                quota_used=0.0,
                is_active=True,
                description="SiliconFlow DeepSeek OCR - 支持图片和PDF文档识别"
            )
            db.add(ocr_model)
        
        await db.commit()
        print("✅ OCR 模型配置成功！")
        print("\n模型信息:")
        print(f"  名称: DeepSeek OCR")
        print(f"  模型: deepseek-ai/DeepSeek-OCR")
        print(f"  类型: ocr")
        print(f"  API: https://api.siliconflow.cn/v1")
        print(f"  配额: 1,000,000 tokens")
        print("\n现在你可以在聊天界面上传图片或 PDF 文件进行识别！")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 初始化 DeepSeek OCR 模型")
    print("=" * 60)
    asyncio.run(init_ocr_model())
    print("=" * 60)
