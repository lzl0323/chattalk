"""
Embedding 服务 - 使用硅基流动 API 调用 BAAI/bge-large-zh-v1.5 模型
"""
import httpx
import logging
from typing import List
from ..core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding 向量化服务"""
    
    def __init__(self):
        self.api_key = settings.embedding_api_key
        self.api_base = settings.embedding_api_base
        self.model = settings.embedding_model
        self.dimension = settings.embedding_dimension
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        获取多个文本的 embedding 向量（批量，自动分批）
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表 [[float, ...], ...]
        """
        if not texts:
            return []
        
        # 硅基流动 API 限制：每次最多 32 个
        BATCH_SIZE = 32
        
        # 如果文本数量超过限制，分批处理
        if len(texts) > BATCH_SIZE:
            logger.info(f"文本数量 {len(texts)} 超过限制，分批处理（每批 {BATCH_SIZE} 个）")
            
            all_embeddings = []
            for i in range(0, len(texts), BATCH_SIZE):
                batch = texts[i:i + BATCH_SIZE]
                logger.info(f"处理第 {i // BATCH_SIZE + 1} 批，共 {len(batch)} 个文本")
                
                batch_embeddings = await self._get_embeddings_single_batch(batch)
                all_embeddings.extend(batch_embeddings)
            
            logger.info(f"所有批次处理完成，共 {len(all_embeddings)} 个向量")
            return all_embeddings
        else:
            # 文本数量在限制内，直接处理
            return await self._get_embeddings_single_batch(texts)
    
    async def _get_embeddings_single_batch(self, texts: List[str]) -> List[List[float]]:
        """
        获取单批文本的 embedding（内部方法）
        
        Args:
            texts: 文本列表（不超过 32 个）
            
        Returns:
            向量列表
        """
        url = f"{self.api_base}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": texts,
            "encoding_format": "float"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                embeddings = [item["embedding"] for item in data["data"]]
                
                logger.info(f"成功生成 {len(embeddings)} 个向量")
                return embeddings
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting embeddings: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Embedding API 错误: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            raise Exception(f"获取 embedding 失败: {str(e)}")
    
    async def get_embedding(self, text: str) -> List[float]:
        """
        获取单个文本的 embedding 向量
        
        Args:
            text: 文本内容
            
        Returns:
            向量 [float, ...]
        """
        embeddings = await self.get_embeddings([text])
        return embeddings[0] if embeddings else []


# 全局实例
embedding_service = EmbeddingService()
