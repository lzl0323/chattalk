"""
RAG (Retrieval-Augmented Generation) 服务
"""
import logging
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.config import settings
from ..utils.vector_store import VectorStore
from .embedding_service import embedding_service

logger = logging.getLogger(__name__)


class RAGService:
    """RAG 检索增强生成服务"""
    
    # RAG Prompt 模板
    RAG_PROMPT_TEMPLATE = """你是一个知识检索增强的智能助手。

以下是与你问题最相关的参考知识片段：

{retrieved_context}

请基于以上内容回答用户问题。如果文档中没有相关信息，请明确回答"文档中没有找到相关内容"，不要编造。

用户问题：
{query}"""
    
    def __init__(self):
        self.vector_stores: Dict[str, VectorStore] = {}
    
    def get_vector_store(self, knowledge_base_id: str = "default") -> VectorStore:
        """
        获取或创建向量存储实例
        
        Args:
            knowledge_base_id: 知识库ID
            
        Returns:
            VectorStore 实例
        """
        if knowledge_base_id not in self.vector_stores:
            self.vector_stores[knowledge_base_id] = VectorStore(
                dimension=settings.embedding_dimension,
                knowledge_base_id=knowledge_base_id,
                storage_path=settings.vector_store_path
            )
        
        return self.vector_stores[knowledge_base_id]
    
    async def retrieve_context(
        self,
        query: str,
        knowledge_base_id: str = "default",
        top_k: int = None,
        similarity_threshold: float = None
    ) -> List[Dict]:
        """
        检索相关上下文
        
        Args:
            query: 用户查询
            knowledge_base_id: 知识库ID
            top_k: 返回结果数量
            similarity_threshold: 相似度阈值
            
        Returns:
            检索结果列表 [{"text": "", "doc_id": "", "similarity": 0.8}, ...]
        """
        if top_k is None:
            top_k = settings.rag_top_k
        if similarity_threshold is None:
            similarity_threshold = settings.rag_similarity_threshold
        
        try:
            # 1. 获取查询向量
            logger.info(f"Generating embedding for query: {query[:100]}...")
            query_vector = await embedding_service.get_embedding(query)
            
            # 2. 向量检索
            logger.info(f"Searching in knowledge base: {knowledge_base_id}")
            vector_store = self.get_vector_store(knowledge_base_id)
            search_results = vector_store.search(
                query_vector=query_vector,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            # 3. 格式化结果
            contexts = []
            for metadata, distance in search_results:
                # 距离转相似度
                similarity = 1 / (1 + distance)
                
                contexts.append({
                    "text": metadata["text"],
                    "doc_id": metadata["doc_id"],
                    "chunk_id": metadata["chunk_id"],
                    "similarity": round(similarity, 4),
                    "distance": round(distance, 4)
                })
            
            logger.info(f"Retrieved {len(contexts)} relevant contexts")
            return contexts
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            raise
    
    def build_rag_prompt(self, query: str, contexts: List[Dict]) -> str:
        """
        构建 RAG Prompt
        
        Args:
            query: 用户查询
            contexts: 检索到的上下文
            
        Returns:
            完整的 RAG Prompt
        """
        if not contexts:
            return query
        
        # 格式化上下文
        context_texts = []
        for i, ctx in enumerate(contexts, 1):
            context_texts.append(
                f"[参考文档 {i}] (相似度: {ctx['similarity']:.2%})\n{ctx['text']}\n"
            )
        
        retrieved_context = "\n".join(context_texts)
        
        # 填充模板
        prompt = self.RAG_PROMPT_TEMPLATE.format(
            retrieved_context=retrieved_context,
            query=query
        )
        
        return prompt
    
    async def add_document(
        self,
        doc_id: str,
        text: str,
        knowledge_base_id: str = "default",
        metadata: Optional[Dict] = None
    ):
        """
        添加文档到向量库
        
        Args:
            doc_id: 文档ID
            text: 文档文本
            knowledge_base_id: 知识库ID
            metadata: 额外元数据
        """
        try:
            # 1. 文本分块
            logger.info(f"Chunking document {doc_id}, length: {len(text)}")
            chunks = self._chunk_text(text)
            
            if not chunks:
                logger.warning(f"Document {doc_id} has no valid chunks")
                return
            
            # 2. 生成 chunk IDs
            chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            
            # 3. 生成 embeddings
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            embeddings = await embedding_service.get_embeddings(chunks)
            
            # 4. 添加到向量库
            vector_store = self.get_vector_store(knowledge_base_id)
            extra_metadata = [{"source": metadata} for _ in chunks] if metadata else None
            
            vector_store.add_vectors(
                vectors=embeddings,
                doc_id=doc_id,
                chunk_ids=chunk_ids,
                texts=chunks,
                extra_metadata=extra_metadata
            )
            
            logger.info(f"Successfully added document {doc_id} to knowledge base {knowledge_base_id}")
            
        except Exception as e:
            logger.error(f"Error adding document {doc_id}: {e}")
            raise
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        文本分块
        
        Args:
            text: 文本内容
            
        Returns:
            分块后的文本列表
        """
        chunk_size = settings.chunk_size
        chunk_overlap = settings.chunk_overlap
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # 取当前块
            chunk = text[start:end]
            
            # 如果不是最后一块，尝试在句号、问号、感叹号等位置切分
            if end < len(text):
                # 查找最后一个句子结束符
                for sep in ['。', '！', '？', '\n', '.', '!', '?']:
                    last_sep = chunk.rfind(sep)
                    if last_sep > chunk_size // 2:  # 确保不切得太短
                        chunk = chunk[:last_sep + 1]
                        end = start + len(chunk)
                        break
            
            chunks.append(chunk.strip())
            start = end - chunk_overlap
        
        return [c for c in chunks if c]  # 过滤空块
    
    def delete_document(self, doc_id: str, knowledge_base_id: str = "default"):
        """
        删除文档
        
        Args:
            doc_id: 文档ID
            knowledge_base_id: 知识库ID
        """
        vector_store = self.get_vector_store(knowledge_base_id)
        vector_store.delete_document(doc_id)
        logger.info(f"Deleted document {doc_id} from knowledge base {knowledge_base_id}")
    
    def get_knowledge_base_stats(self, knowledge_base_id: str = "default") -> Dict:
        """
        获取知识库统计信息
        
        Args:
            knowledge_base_id: 知识库ID
            
        Returns:
            统计信息
        """
        vector_store = self.get_vector_store(knowledge_base_id)
        return vector_store.get_stats()


# 全局实例
rag_service = RAGService()
