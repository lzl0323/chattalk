"""Kimi API 服务"""

import httpx
import json
import logging
from typing import AsyncGenerator, List, Dict, Optional
from ..core.config import settings

logger = logging.getLogger(__name__)


class KimiService:
    """Kimi API 服务类"""
    
    def __init__(self):
        self.api_key = settings.kimi_api_key
        self.api_base = settings.kimi_api_base
        self.default_model = settings.kimi_model
        
        # 创建异步 HTTP 客户端
        self.client = httpx.AsyncClient(
            timeout=300.0,  # 5 分钟超时
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Yields:
            响应内容块
        """
        model = model or self.default_model
        
        request_data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        logger.info(f"Calling Kimi API with model: {model}, messages count: {len(messages)}")
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.api_base}/chat/completions",
                json=request_data
            ) as response:
                
                # 检查响应状态
                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(f"Kimi API error: {response.status_code} - {error_text.decode()}")
                    raise Exception(f"Kimi API 返回错误: {response.status_code}")
                
                # 流式读取响应
                async for line in response.aiter_lines():
                    # 跳过空行
                    if not line.strip():
                        continue
                    
                    # SSE 格式：data: {...}
                    if line.startswith("data: "):
                        data = line[6:]  # 移除 "data: " 前缀
                        
                        # 检查是否是结束标记
                        if data.strip() == "[DONE]":
                            logger.info("Stream completed")
                            break
                        
                        try:
                            # 解析 JSON
                            chunk = json.loads(data)
                            
                            # 提取内容
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                
                                if content:
                                    yield content
                                    
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse JSON chunk: {data}, error: {e}")
                            continue
                        
        except httpx.TimeoutException:
            logger.error("Kimi API request timeout")
            raise Exception("请求超时，请稍后重试")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in chat_stream: {e}", exc_info=True)
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        非流式聊天
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Returns:
            完整的响应内容
        """
        model = model or self.default_model
        
        request_data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        logger.info(f"Calling Kimi API (non-stream) with model: {model}")
        
        try:
            response = await self.client.post(
                f"{self.api_base}/chat/completions",
                json=request_data
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            # 提取响应内容
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception("Kimi API 返回格式错误")
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in chat: {e}")
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in chat: {e}", exc_info=True)
            raise
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()


# 全局 Kimi 服务实例
kimi_service = KimiService()
