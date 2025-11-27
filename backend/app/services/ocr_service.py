"""
OCR 服务 - 使用 SiliconFlow DeepSeek-OCR 模型
"""
import base64
import logging
from typing import Optional, Dict, Any
from openai import OpenAI

from ..core.encryption import decrypt_api_key
from ..models.db_models import ModelConfig

logger = logging.getLogger(__name__)


class OCRService:
    """OCR 识别服务"""
    
    # OCR 模式对应的 prompt
    OCR_PROMPTS = {
        "markdown": "Convert the document to markdown.",
        "general": "Extract all text from this document.",
        "free_ocr": "Extract text content only, no formatting.",
        "chart": "Extract and describe all charts, tables and diagrams in this document.",
        "describe": "Describe the content and layout of this document in detail.",
        "locate": "Identify and locate all text regions in this document."
    }
    
    def __init__(self, model_config: ModelConfig):
        """
        初始化 OCR 服务
        
        Args:
            model_config: OCR 模型配置
        """
        self.model_config = model_config
        
        # 解密 API Key
        api_key = decrypt_api_key(model_config.api_key_encrypted)
        
        # 创建 OpenAI 客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url=model_config.api_base
        )
    
    def process_file(
        self,
        file_content: bytes,
        file_type: str,
        ocr_mode: str = "markdown"
    ) -> Dict[str, Any]:
        """
        处理文件进行 OCR 识别
        
        Args:
            file_content: 文件二进制内容
            file_type: 文件类型 (image/jpeg, image/png, application/pdf)
            ocr_mode: OCR 模式
            
        Returns:
            {
                "success": True/False,
                "content": "识别结果",
                "error": "错误信息"
            }
        """
        try:
            # 将文件转为 base64
            base64_data = base64.b64encode(file_content).decode("utf-8")
            
            # 构建 data URL
            if file_type in ["image/jpeg", "image/jpg"]:
                data_url = f"data:image/jpeg;base64,{base64_data}"
            elif file_type == "image/png":
                data_url = f"data:image/png;base64,{base64_data}"
            elif file_type == "application/pdf":
                data_url = f"data:application/pdf;base64,{base64_data}"
            else:
                return {
                    "success": False,
                    "content": "",
                    "error": f"不支持的文件类型: {file_type}"
                }
            
            # 获取对应的 prompt
            prompt = self.OCR_PROMPTS.get(ocr_mode, self.OCR_PROMPTS["markdown"])
            
            # 构建请求消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url
                            }
                        },
                        {
                            "type": "text",
                            "text": f"<image>\n<|grounding|>{prompt}"
                        }
                    ]
                }
            ]
            
            logger.info(f"Calling OCR API with mode: {ocr_mode}")
            
            # 调用 OCR API
            response = self.client.chat.completions.create(
                model=self.model_config.model,
                messages=messages,
                temperature=0.1,  # OCR 任务使用低温度
                max_tokens=4096,
                stream=False
            )
            
            # 提取识别结果
            content = response.choices[0].message.content
            
            logger.info(f"OCR success, content length: {len(content)}")
            
            return {
                "success": True,
                "content": content,
                "error": None,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"OCR failed: {error_msg}")
            
            # 检查是否是配额不足
            if "insufficient" in error_msg.lower() or "quota" in error_msg.lower():
                return {
                    "success": False,
                    "content": "",
                    "error": "MODEL_USAGE_EXCEEDED"
                }
            
            return {
                "success": False,
                "content": "",
                "error": error_msg
            }
    
    @staticmethod
    def validate_file(file_content: bytes, file_type: str) -> tuple[bool, str]:
        """
        验证文件
        
        Returns:
            (是否有效, 错误信息)
        """
        # 检查文件大小 (最大 10MB)
        max_size = 10 * 1024 * 1024
        if len(file_content) > max_size:
            return False, "文件大小超过 10MB 限制"
        
        # 检查文件类型
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "application/pdf"]
        if file_type not in allowed_types:
            return False, f"不支持的文件类型: {file_type}"
        
        return True, ""
