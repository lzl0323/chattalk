"""
智能推荐问题生成服务
基于用户兴趣、技术热点、科研趋势生成推荐问题
"""
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.db_models import Conversation, Message, ModelConfig, SuggestionRecord
from ..services.openai_service import openai_client_service
from ..services.trending_fetcher import trending_fetcher

logger = logging.getLogger(__name__)


class SuggestionService:
    """推荐问题生成服务"""
    
    # 默认技术热点（可以通过外部API获取）
    DEFAULT_TRENDING_TOPICS = [
        "GPT-4", "Claude 3", "Llama 3", "Mistral AI",
        "React 19", "Vue 3.4", "Next.js 14", "TypeScript 5.3",
        "FastAPI", "Django 5.0", "Python 3.12",
        "Docker", "Kubernetes", "微服务架构",
        "WebAssembly", "Edge Computing", "Serverless"
    ]
    
    # 默认科研趋势
    DEFAULT_RESEARCH_TRENDS = [
        "Large Language Models", "Multimodal AI", "Diffusion Models",
        "Retrieval-Augmented Generation (RAG)", "Vision-Language Models",
        "3D Reconstruction", "Neural Radiance Fields",
        "Reinforcement Learning from Human Feedback",
        "Few-shot Learning", "Transfer Learning"
    ]
    
    # 通用科技话题
    GENERAL_TOPICS = [
        "如何学习编程", "前端开发最佳实践", "后端架构设计",
        "数据库优化技巧", "AI应用开发", "云原生技术",
        "DevOps实践", "网络安全", "性能优化", "代码重构"
    ]
    
    @staticmethod
    async def get_user_recent_topics(db: AsyncSession, user_id: int, days: int = 7) -> List[str]:
        """
        获取用户最近的聊天主题
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 最近几天
            
        Returns:
            主题列表
        """
        try:
            threshold = datetime.now() - timedelta(days=days)
            
            # 获取用户最近的对话
            result = await db.execute(
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .where(Conversation.updated_at >= threshold)
                .order_by(Conversation.updated_at.desc())
                .limit(10)
            )
            conversations = result.scalars().all()
            
            # 提取对话标题作为主题
            topics = []
            for conv in conversations:
                if conv.title and conv.title != "新对话":
                    topics.append(conv.title)
            
            return topics[:5]  # 最多返回5个主题
            
        except Exception as e:
            logger.error(f"Failed to get user recent topics: {e}")
            return []
    
    @staticmethod
    async def generate_suggestions_with_ai(
        db: AsyncSession,
        user_id: int,
        count: int = 6,
        trending_topics: Optional[List[str]] = None,
        research_trends: Optional[List[str]] = None,
        use_ai: bool = False  # 默认使用后备推荐（速度快，质量好）
    ) -> List[Dict[str, str]]:
        """
        使用AI生成推荐问题
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            count: 推荐数量
            trending_topics: 技术热点列表
            research_trends: 科研趋势列表
            use_ai: 是否使用AI生成（默认True，已优化速度至5-10秒）
            
        Returns:
            推荐问题列表
        """
        # 如果不使用 AI，直接返回后备推荐（速度快）
        if not use_ai:
            return await SuggestionService.get_fallback_suggestions(db, user_id, count)
        
        try:
            # 获取用户最近的主题
            recent_topics = await SuggestionService.get_user_recent_topics(db, user_id)
            
            # 使用默认值
            if not trending_topics:
                trending_topics = SuggestionService.DEFAULT_TRENDING_TOPICS[:10]
            if not research_trends:
                research_trends = SuggestionService.DEFAULT_RESEARCH_TRENDS[:8]
            
            # 构建提示词
            prompt = SuggestionService._build_prompt(
                recent_topics=recent_topics,
                trending_topics=trending_topics,
                research_trends=research_trends,
                count=count
            )
            
            # 获取一个激活的模型配置
            from ..services.model_config_service import ModelConfigService
            configs, _ = await ModelConfigService.get_model_configs(db, limit=1, active_only=True)
            
            if not configs:
                logger.warning("No active model config found, using fallback suggestions")
                return SuggestionService.get_fallback_suggestions(count)
            
            config = configs[0]
            
            # 解密API密钥
            from ..core.encryption import encryption_service
            try:
                api_key = encryption_service.decrypt(config.api_key_encrypted)
            except Exception as e:
                logger.error(f"Failed to decrypt API key: {e}")
                return SuggestionService.get_fallback_suggestions(count)
            
            # 调用AI生成（优化参数提升速度）
            messages = [
                {"role": "system", "content": "生成JSON格式的技术问题推荐"},
                {"role": "user", "content": prompt}
            ]
            
            # 使用超时控制
            import asyncio
            try:
                # 创建客户端，设置更短的超时
                from openai import AsyncOpenAI
                client = AsyncOpenAI(
                    api_key=api_key,
                    base_url=config.api_base,
                    timeout=8.0  # 8秒超时
                )
                
                response = await asyncio.wait_for(
                    client.chat.completions.create(
                        model=config.model,
                        messages=messages,
                        temperature=0.7,  # 降低温度，更快
                        max_tokens=300,  # 限制输出长度
                        stream=False
                    ),
                    timeout=10.0  # 总超时10秒
                )
            except asyncio.TimeoutError:
                logger.warning("AI suggestion generation timed out")
                return SuggestionService.get_fallback_suggestions(count)
            except Exception as e:
                logger.error(f"AI generation failed: {e}")
                return SuggestionService.get_fallback_suggestions(count)
            
            content = response.choices[0].message.content
            
            # 解析JSON响应
            suggestions = SuggestionService._parse_ai_response(content, count)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions with AI: {e}", exc_info=True)
            return SuggestionService.get_fallback_suggestions(count)
    
    @staticmethod
    def _build_prompt(
        recent_topics: List[str],
        trending_topics: List[str],
        research_trends: List[str],
        count: int
    ) -> str:
        """构建AI提示词（精简版，提升响应速度）"""
        # 简化提示词，减少token数量
        recent = ', '.join(recent_topics[:3]) if recent_topics else '无'
        trending = ', '.join(trending_topics[:5])
        research = ', '.join(research_trends[:3])
        
        prompt = f"""生成{count}个技术问题推荐，每条不超过15字。

热点: {trending}
科研: {research}
用户兴趣: {recent}

直接输出JSON:
{{"suggestions":[{{"type":"trending","title":"问题","icon":"bolt"}}]}}"""
        
        return prompt
    
    @staticmethod
    def _parse_ai_response(content: str, count: int) -> List[Dict[str, str]]:
        """解析AI响应"""
        try:
            # 清理可能的markdown代码块
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # 解析JSON
            data = json.loads(content)
            suggestions = data.get("suggestions", [])
            
            # 验证和限制数量
            valid_suggestions = []
            for s in suggestions[:count]:
                if "title" in s and len(s["title"]) <= 30:
                    valid_suggestions.append({
                        "type": s.get("type", "general"),
                        "title": s["title"],
                        "icon": s.get("icon", "bolt")
                    })
            
            return valid_suggestions if valid_suggestions else SuggestionService.get_fallback_suggestions(count)
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return SuggestionService.get_fallback_suggestions(count)
    
    @staticmethod
    async def get_recent_suggestions(db: AsyncSession, user_id: int, days: int = 7) -> List[str]:
        """
        获取用户最近推荐过的问题标题
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 最近几天
            
        Returns:
            最近推荐的标题列表
        """
        try:
            threshold = datetime.now() - timedelta(days=days)
            result = await db.execute(
                select(SuggestionRecord.title)
                .where(and_(
                    SuggestionRecord.user_id == user_id,
                    SuggestionRecord.created_at >= threshold
                ))
            )
            titles = [row[0] for row in result.all()]
            return titles
        except Exception as e:
            logger.error(f"Failed to get recent suggestions: {e}")
            return []
    
    @staticmethod
    async def save_suggestions(
        db: AsyncSession,
        user_id: int,
        suggestions: List[Dict[str, str]]
    ) -> None:
        """
        保存推荐记录到数据库
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            suggestions: 推荐问题列表
        """
        try:
            for suggestion in suggestions:
                record = SuggestionRecord(
                    user_id=user_id,
                    suggestion_type=suggestion.get("type", "general"),
                    title=suggestion.get("title", ""),
                    icon=suggestion.get("icon", "bolt")
                )
                db.add(record)
            
            await db.commit()
            logger.info(f"Saved {len(suggestions)} suggestions for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to save suggestions: {e}")
            await db.rollback()
    
    @staticmethod
    async def get_fallback_suggestions(
        db: Optional[AsyncSession] = None,
        user_id: Optional[int] = None,
        count: int = 6
    ) -> List[Dict[str, str]]:
        """获取推荐问题（结合静态问题池和动态热点，避免重复）"""
        import random
        
        # 1. 获取动态热点问题（每6小时更新）
        try:
            dynamic_suggestions = await trending_fetcher.get_dynamic_suggestions(count=10)
        except Exception as e:
            logger.error(f"Failed to get dynamic suggestions: {e}")
            dynamic_suggestions = []
        
        # 2. 精选静态问题池（扩展到20+个）
        static_suggestions = [
            # 技术热点
            {"type": "trending", "title": "GPT-4 vs Claude 3 对比", "icon": "bolt"},
            {"type": "trending", "title": "Next.js 14 新特性解读", "icon": "bolt"},
            {"type": "trending", "title": "React 19 Server Components", "icon": "bolt"},
            {"type": "trending", "title": "Vue 3.4 性能优化技巧", "icon": "bolt"},
            {"type": "trending", "title": "TypeScript 5.3 新特性", "icon": "bolt"},
            {"type": "trending", "title": "Rust 在前端的应用", "icon": "bolt"},
            {"type": "trending", "title": "WebAssembly 实战指南", "icon": "bolt"},
            
            # 科研前沿
            {"type": "research", "title": "RAG 技术原理与应用", "icon": "science"},
            {"type": "research", "title": "多模态 AI 模型详解", "icon": "science"},
            {"type": "research", "title": "Diffusion Models 工作原理", "icon": "science"},
            {"type": "research", "title": "LLM 微调最佳实践", "icon": "science"},
            {"type": "research", "title": "强化学习在 NLP 中的应用", "icon": "science"},
            {"type": "research", "title": "神经网络压缩技术", "icon": "science"},
            
            # 实用技巧
            {"type": "general", "title": "前端性能优化指南", "icon": "lightbulb"},
            {"type": "general", "title": "微服务架构设计要点", "icon": "lightbulb"},
            {"type": "general", "title": "Python 异步编程实战", "icon": "code"},
            {"type": "general", "title": "Docker 容器化部署", "icon": "server"},
            {"type": "general", "title": "API 设计最佳实践", "icon": "api"},
            {"type": "general", "title": "数据库查询优化技巧", "icon": "database"},
            {"type": "general", "title": "Git 进阶使用技巧", "icon": "code"},
            {"type": "general", "title": "Nginx 配置优化", "icon": "server"},
            {"type": "general", "title": "Redis 缓存策略", "icon": "database"},
            {"type": "general", "title": "测试驱动开发实践", "icon": "code"},
        ]
        
        # 3. 合并动态和静态问题（动态优先）
        all_suggestions = dynamic_suggestions + static_suggestions
        
        # 4. 如果提供了数据库和用户ID，排除最近7天推荐过的
        if db and user_id:
            recent_titles = await SuggestionService.get_recent_suggestions(db, user_id, days=7)
            # 过滤掉最近推荐过的
            available = [s for s in all_suggestions if s["title"] not in recent_titles]
            # 如果过滤后太少，重新使用全部
            if len(available) < count:
                logger.info("Not enough unique suggestions, reusing all")
                available = all_suggestions
        else:
            available = all_suggestions
        
        # 5. 随机选择，每次显示不同的推荐
        selected = random.sample(available, min(count, len(available)))
        
        logger.info(f"Generated suggestions: {len(dynamic_suggestions)} dynamic + {len(static_suggestions)} static = {len(all_suggestions)} total, selected {len(selected)}")
        return selected
