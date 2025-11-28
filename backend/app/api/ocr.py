"""
OCR 相关 API 接口
"""
import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.database import get_db
from ..core.auth import get_current_user
from ..models.db_models import User, ModelConfig, Conversation, Message
from ..services.ocr_service import OCRService
from ..core.encryption import decrypt_api_key

router = APIRouter(prefix="/api/ocr", tags=["OCR"])


@router.post("/upload")
async def upload_and_ocr(
    file: UploadFile = File(...),
    conversation_id: str = Form(...),
    ocr_mode: str = Form(default="markdown"),
    model_id: Optional[int] = Form(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上传文件并进行 OCR 识别
    
    Args:
        file: 上传的文件
        conversation_id: 对话 ID
        ocr_mode: OCR 模式 (markdown/general/free_ocr/chart/describe/locate)
        model_id: OCR 模型 ID（可选，不提供则使用默认 OCR 模型）
        
    Returns:
        {
            "message_id": int,
            "content_markdown": str,
            "ocr_mode": str,
            "file_url": str
        }
    """
    
    # 1. 验证对话是否属于当前用户
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 2. 读取文件内容
    file_content = await file.read()
    file_type = file.content_type
    
    # 3. 验证文件
    from ..services.ocr_service import OCRService as OCR
    is_valid, error_msg = OCR.validate_file(file_content, file_type)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 4. 获取 OCR 模型配置
    if model_id:
        # 使用指定模型
        result = await db.execute(
            select(ModelConfig).where(
                ModelConfig.id == model_id,
                ModelConfig.model_type == "ocr",
                ModelConfig.is_active == True
            )
        )
    else:
        # 使用默认 OCR 模型
        result = await db.execute(
            select(ModelConfig).where(
                ModelConfig.model_type == "ocr",
                ModelConfig.is_active == True
            ).order_by(ModelConfig.id).limit(1)
        )
    
    ocr_model = result.scalar_one_or_none()
    
    if not ocr_model:
        raise HTTPException(status_code=404, detail="没有可用的 OCR 模型")
    
    # 检查配额
    if ocr_model.is_quota_exceeded():
        raise HTTPException(
            status_code=429,
            detail={"error": "MODEL_USAGE_EXCEEDED", "message": "OCR 模型配额已用尽"}
        )
    
    # 5. 保存文件到本地
    # 使用绝对路径保存文件
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_dir = os.path.join(backend_dir, "uploads", "ocr", str(current_user.id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # 生成用于前端访问的 URL 路径（使用正斜杠）
    file_url = f"/uploads/ocr/{current_user.id}/{unique_filename}"
    
    # 6. 调用 OCR 服务
    ocr_service = OCRService(ocr_model)
    ocr_result = ocr_service.process_file(file_content, file_type, ocr_mode)
    
    if not ocr_result["success"]:
        # OCR 失败，删除文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail={"error": ocr_result["error"], "message": "OCR 识别失败"}
        )
    
    # 7. 更新模型配额
    if ocr_result.get("tokens_used"):
        ocr_model.increment_quota(ocr_result["tokens_used"])
        await db.commit()
    
    # 8. 保存用户上传文件的消息（图片预览）
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=f"[上传文件: {file.filename}]",
        message_type="image",
        file_url=file_url,  # 使用 URL 路径而不是文件系统路径
        file_name=file.filename,
        ocr_mode=ocr_mode
    )
    db.add(user_message)
    await db.commit()
    
    # 9. 不保存 OCR 识别结果为消息
    # 而是直接返回给前端，由前端自动发送给聊天模型
    # 这样可以让聊天模型基于识别内容进行智能回复
    
    # 10. 更新对话的最后更新时间
    from datetime import datetime
    conversation.updated_at = datetime.now()
    await db.commit()
    
    return {
        "content_markdown": ocr_result["content"],
        "ocr_mode": ocr_mode,
        "file_url": file_url,  # 返回 URL 路径
        "file_name": file.filename,
        "user_message_id": user_message.id
    }


@router.get("/models")
async def get_ocr_models(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取所有可用的 OCR 模型
    
    Returns:
        [
            {
                "id": int,
                "name": str,
                "model": str,
                "is_active": bool,
                "quota_percentage": float
            }
        ]
    """
    result = await db.execute(
        select(ModelConfig).where(
            ModelConfig.model_type == "ocr"
        ).order_by(ModelConfig.id)
    )
    models = result.scalars().all()
    
    return [
        {
            "id": m.id,
            "name": m.name,
            "model": m.model,
            "is_active": m.is_active and not m.is_quota_exceeded(),
            "quota_percentage": m.quota_percentage,
            "quota_remaining": m.quota_remaining
        }
        for m in models
    ]


@router.get("/modes")
async def get_ocr_modes():
    """
    获取所有支持的 OCR 模式
    """
    return {
        "modes": [
            {
                "value": "markdown",
                "label": "文档转 Markdown",
                "description": "将文档转换为结构化的 Markdown 格式",
                "icon": "📄"
            },
            {
                "value": "general",
                "label": "通用 OCR",
                "description": "提取文档中的所有文本内容",
                "icon": "📝"
            },
            {
                "value": "free_ocr",
                "label": "纯文本提取",
                "description": "仅提取纯文本，不保留格式",
                "icon": "📋"
            },
            {
                "value": "chart",
                "label": "图表解析",
                "description": "识别并描述文档中的图表、表格",
                "icon": "📊"
            },
            {
                "value": "describe",
                "label": "文档描述",
                "description": "详细描述文档的内容和布局",
                "icon": "🔍"
            },
            {
                "value": "locate",
                "label": "文字定位",
                "description": "识别和定位文档中的文字区域",
                "icon": "📍"
            }
        ]
    }
