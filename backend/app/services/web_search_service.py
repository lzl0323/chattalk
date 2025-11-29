"""
Web Search 服务 - 支持联网搜索
"""
import httpx
import logging
from typing import List, Dict, Optional
from ..core.config import settings

logger = logging.getLogger(__name__)


class WebSearchService:
    """Web 搜索服务"""
    
    def __init__(self):
        self.tavily_api_key = getattr(settings, 'tavily_api_key', None)
        self.use_tavily = bool(self.tavily_api_key)
        
        # 启动时显示配置状态
        if self.use_tavily:
            logger.info(f"✅ Tavily API 已配置 (Key: {self.tavily_api_key[:10]}...)")
        else:
            logger.warning("⚠️  Tavily API 未配置，将使用 DuckDuckGo（免费但质量较差）")
    
    async def search_tavily(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        使用 Tavily API 搜索（推荐）
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        if not self.tavily_api_key:
            raise Exception("Tavily API key not configured")
        
        url = "https://api.tavily.com/search"
        
        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",  # basic 或 advanced
            "include_answer": True,  # 包含 AI 生成的答案
            "include_raw_content": False,
            "include_images": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                
                results = []
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", ""),
                        "score": item.get("score", 0.0)
                    })
                
                # 如果有 AI 生成的答案，也包含进去
                if data.get("answer"):
                    results.insert(0, {
                        "title": "AI Summary",
                        "url": "",
                        "content": data["answer"],
                        "score": 1.0
                    })
                
                logger.info(f"Tavily search returned {len(results)} results for: {query}")
                return results
                
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            raise
    
    async def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        使用 DuckDuckGo 搜索（免费，无需 API Key）
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        try:
            from ddgs import DDGS
            
            results = []
            
            # 优化搜索查询（添加时间相关关键词）
            optimized_query = query
            if any(keyword in query for keyword in ['今天', '现在', '当前', '最新']):
                optimized_query = f"{query} 2025年11月"
            
            logger.info(f"优化后的查询: {optimized_query}")
            
            # 使用同步方式搜索
            with DDGS() as ddgs:
                search_results = list(ddgs.text(optimized_query, max_results=max_results))
                
                for item in search_results:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("href", ""),
                        "content": item.get("body", ""),
                        "score": 0.5  # DuckDuckGo 不提供相关性分数
                    })
            
            logger.info(f"DuckDuckGo search returned {len(results)} results for: {query}")
            return results
            
        except ImportError:
            logger.error("ddgs not installed. Run: pip install ddgs")
            raise Exception("DuckDuckGo search requires: pip install ddgs")
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            raise
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        智能搜索：优先使用 Tavily，降级到 DuckDuckGo
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        # 优先使用 Tavily
        if self.use_tavily:
            try:
                return await self.search_tavily(query, max_results)
            except Exception as e:
                logger.warning(f"Tavily failed, falling back to DuckDuckGo: {e}")
        
        # 降级到 DuckDuckGo
        try:
            return await self.search_duckduckgo(query, max_results)
        except Exception as e:
            logger.error(f"All search methods failed: {e}")
            return []
    
    def build_search_prompt(self, query: str, search_results: List[Dict]) -> str:
        """
        构建基于搜索结果的 Prompt
        
        Args:
            query: 用户查询
            search_results: 搜索结果
            
        Returns:
            增强后的 Prompt
        """
        if not search_results:
            return query
        
        prompt_parts = ["你是一个联网搜索增强的智能助手。\n"]
        prompt_parts.append("我已经为你从互联网搜索到以下最新信息：\n")
        
        for i, result in enumerate(search_results, 1):
            prompt_parts.append(f"\n[搜索结果 {i}]")
            if result["title"]:
                prompt_parts.append(f"标题: {result['title']}")
            if result["url"]:
                prompt_parts.append(f"来源: {result['url']}")
            if result["content"]:
                # 限制每个结果的长度（减少到300字符避免API错误）
                content = result["content"][:300]
                prompt_parts.append(f"内容: {content}")
            prompt_parts.append("")
        
        prompt_parts.append(f"\n⚠️ 重要提示：")
        prompt_parts.append(f"1. 请仔细检查搜索结果是否与问题相关")
        prompt_parts.append(f"2. 如果搜索结果不相关或无用，请明确告知用户：'抱歉，搜索结果不够准确，无法回答这个问题'")
        prompt_parts.append(f"3. 不要根据无关内容编造答案")
        prompt_parts.append(f"4. 如果是询问时间日期的问题，请特别注意搜索结果中的时间信息")
        prompt_parts.append(f"\n用户问题：\n{query}")
        
        return "\n".join(prompt_parts)


# 全局实例
web_search_service = WebSearchService()
