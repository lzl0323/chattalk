"""
初始化 DeepSeek OCR 模型配置
运行此脚本添加 OCR 模型到数据库
"""
import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker
from app.models.db_models import ModelConfig
from app.core.encryption import encrypt_api_key

# 加载环境变量
load_dotenv()

async def init_ocr_model():
    """添加 DeepSeek OCR 模型配置"""
    
    # 从环境变量读取 OCR 模型配置
    api_key = os.getenv(
        "DEEPSEEK_OCR_API_KEY",
        "sk-ayghpphczpwrrstumeodmfxefwnxfokudjmwqspvskjaapep"  # 默认值（备用）
    )
    api_base = os.getenv(
        "DEEPSEEK_OCR_API_BASE",
        "https://api.siliconflow.cn/v1"
    )
    model_name = os.getenv(
        "DEEPSEEK_OCR_MODEL",
        "deepseek-ai/DeepSeek-OCR"
    )
    quota_limit = float(os.getenv(
        "DEEPSEEK_OCR_QUOTA_LIMIT",
        "1000000"
    ))
    
    async with async_session_maker() as db:
        # 检查是否已存在
        from sqlalchemy import select
        result = await db.execute(
            select(ModelConfig).where(ModelConfig.name == "DeepSeek OCR")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("✅ DeepSeek OCR 模型已存在，更新配置...")
            existing.model = model_name
            existing.model_type = "ocr"
            existing.api_base = api_base
            existing.api_key_encrypted = encrypt_api_key(api_key)
            existing.quota_limit = quota_limit
            existing.quota_used = 0.0
            existing.is_active = True
            existing.description = "SiliconFlow DeepSeek OCR - 支持图片和PDF文档识别"
        else:
            print("📦 添加新的 DeepSeek OCR 模型配置...")
            ocr_model = ModelConfig(
                name="DeepSeek OCR",
                model=model_name,
                model_type="ocr",
                api_base=api_base,
                api_key_encrypted=encrypt_api_key(api_key),
                quota_limit=quota_limit,
                quota_used=0.0,
                is_active=True,
                description="SiliconFlow DeepSeek OCR - 支持图片和PDF文档识别"
            )
            db.add(ocr_model)
        
        await db.commit()
        print("✅ OCR 模型配置成功！")
        print("\n模型信息:")
        print(f"  名称: DeepSeek OCR")
        print(f"  模型: {model_name}")
        print(f"  类型: ocr")
        print(f"  API: {api_base}")
        print(f"  配额: {quota_limit:,.0f} tokens")
        print("\n现在你可以在聊天界面上传图片或 PDF 文件进行识别！")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 初始化 DeepSeek OCR 模型")
    print("=" * 60)
    asyncio.run(init_ocr_model())
    print("=" * 60)
