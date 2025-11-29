"""应用配置管理"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # Kimi API 配置
    kimi_api_key: str
    kimi_api_base: str = "https://api.moonshot.cn/v1"
    kimi_model: str = "moonshot-v1-8k"
    
    # 应用配置
    max_context_messages: int = 10
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # JWT 认证配置
    jwt_secret_key: str = "your-secret-key-change-in-production-min-32-characters-long"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24 * 7  # 7天
    
    # 加密配置
    encryption_key: str = "default-encryption-key-change-in-production"
    
    # 速率限制（可选）
    max_requests_per_minute: int = 60
    
    # DeepSeek OCR 配置（可选）
    deepseek_ocr_api_key: str = ""
    deepseek_ocr_api_base: str = "https://api.siliconflow.cn/v1"
    deepseek_ocr_model: str = "deepseek-ai/DeepSeek-OCR"
    deepseek_ocr_quota_limit: float = 1000000.0
    
    # RAG Embedding 配置
    embedding_api_key: str = "sk-toidgawwsnxnxnnoowbbxwzppnljpfpjzkcoutivupcihbis"
    embedding_api_base: str = "https://api.siliconflow.cn/v1"
    embedding_model: str = "BAAI/bge-large-zh-v1.5"
    embedding_dimension: int = 1024
    
    # RAG 配置
    rag_top_k: int = 3
    rag_similarity_threshold: float = 0.7
    vector_store_path: str = "data/vector_index"
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Web Search 配置
    tavily_api_key: str = ""  # Tavily API Key（可选，留空则使用 DuckDuckGo）
    web_search_max_results: int = 3  # 搜索结果数量（减少以避免 Prompt 过长）
    
    @property
    def cors_origins_list(self) -> List[str]:
        """解析 CORS origins 为列表"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
