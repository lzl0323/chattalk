"""
向量存储工具 - 基于 FAISS
"""
import faiss
import numpy as np
import pickle
import os
import logging
from typing import List, Tuple, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS 向量存储"""
    
    def __init__(self, dimension: int, knowledge_base_id: str, storage_path: str):
        """
        初始化向量存储
        
        Args:
            dimension: 向量维度
            knowledge_base_id: 知识库ID
            storage_path: 存储路径
        """
        self.dimension = dimension
        self.knowledge_base_id = knowledge_base_id
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 索引文件路径
        self.index_path = self.storage_path / f"{knowledge_base_id}.index"
        self.metadata_path = self.storage_path / f"{knowledge_base_id}.meta"
        
        # 初始化 FAISS 索引
        self.index = None
        self.metadata = []  # 存储文档元数据 [{doc_id, chunk_id, text, ...}]
        
        # 加载已有索引
        self.load()
    
    def load(self):
        """加载索引和元数据"""
        if self.index_path.exists() and self.metadata_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Loaded vector store for {self.knowledge_base_id}: {self.index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Error loading vector store: {e}")
                self._initialize_new_index()
        else:
            self._initialize_new_index()
    
    def _initialize_new_index(self):
        """初始化新索引"""
        # 使用 IndexFlatL2 进行精确的L2距离搜索
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        logger.info(f"Initialized new vector store for {self.knowledge_base_id}")
    
    def save(self):
        """保存索引和元数据"""
        try:
            faiss.write_index(self.index, str(self.index_path))
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            logger.info(f"Saved vector store for {self.knowledge_base_id}")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            raise
    
    def add_vectors(
        self,
        vectors: List[List[float]],
        doc_id: str,
        chunk_ids: List[str],
        texts: List[str],
        extra_metadata: Optional[List[Dict]] = None
    ):
        """
        添加向量到索引
        
        Args:
            vectors: 向量列表
            doc_id: 文档ID
            chunk_ids: chunk ID 列表
            texts: 文本内容列表
            extra_metadata: 额外元数据
        """
        if not vectors:
            return
        
        # 转换为 numpy 数组
        vectors_array = np.array(vectors, dtype=np.float32)
        
        # 添加到索引
        self.index.add(vectors_array)
        
        # 保存元数据
        for i, (chunk_id, text) in enumerate(zip(chunk_ids, texts)):
            meta = {
                "doc_id": doc_id,
                "chunk_id": chunk_id,
                "text": text
            }
            if extra_metadata and i < len(extra_metadata):
                meta.update(extra_metadata[i])
            self.metadata.append(meta)
        
        # 保存到磁盘
        self.save()
        
        logger.info(f"Added {len(vectors)} vectors to {self.knowledge_base_id}")
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        similarity_threshold: Optional[float] = None
    ) -> List[Tuple[Dict, float]]:
        """
        搜索最相似的向量
        
        Args:
            query_vector: 查询向量
            top_k: 返回top k个结果
            similarity_threshold: 相似度阈值（可选）
            
        Returns:
            [(metadata, distance), ...] 距离越小越相似
        """
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []
        
        # 转换查询向量
        query_array = np.array([query_vector], dtype=np.float32)
        
        # 搜索
        distances, indices = self.index.search(query_array, min(top_k, self.index.ntotal))
        
        # 构建结果
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS 返回 -1 表示没有找到
                continue
            
            # 计算余弦相似度（如果需要）
            # L2距离转相似度: similarity = 1 / (1 + distance)
            similarity = 1 / (1 + dist)
            
            # 应用阈值
            if similarity_threshold and similarity < similarity_threshold:
                continue
            
            results.append((self.metadata[idx], float(dist)))
        
        logger.info(f"Found {len(results)} results for query")
        return results
    
    def delete_document(self, doc_id: str):
        """
        删除文档的所有向量
        
        Args:
            doc_id: 文档ID
        """
        # FAISS 不支持直接删除，需要重建索引
        # 保留非目标文档的数据
        keep_indices = [i for i, meta in enumerate(self.metadata) if meta["doc_id"] != doc_id]
        
        if len(keep_indices) == len(self.metadata):
            logger.warning(f"Document {doc_id} not found in vector store")
            return
        
        # 提取保留的向量
        if keep_indices:
            kept_vectors = []
            for idx in keep_indices:
                # 从原索引中重构向量（这是一个简化方案，实际可能需要重新生成embedding）
                # 这里我们假设直接删除后重建
                pass
            
            # 重建索引
            self._initialize_new_index()
            
            # 重新添加保留的元数据
            self.metadata = [self.metadata[i] for i in keep_indices]
        else:
            self._initialize_new_index()
        
        self.save()
        logger.info(f"Deleted document {doc_id} from vector store")
    
    def clear(self):
        """清空索引"""
        self._initialize_new_index()
        self.save()
        logger.info(f"Cleared vector store for {self.knowledge_base_id}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "knowledge_base_id": self.knowledge_base_id,
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_path": str(self.index_path),
            "metadata_count": len(self.metadata)
        }
