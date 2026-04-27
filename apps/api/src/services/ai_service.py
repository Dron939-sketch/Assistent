"""
AI Service - integration with LLMs (OpenAI, YandexGPT)
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from openai import AsyncOpenAI
from src.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered content generation"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.OPENAI_MAX_TOKENS
    
    async def initialize(self):
        """Initialize service (load prompts, models)"""
        logger.info("AI Service initialized")
    
    async def shutdown(self):
        """Cleanup"""
        await self.client.close()
        logger.info("AI Service shutdown")
    
    async def _get_system_prompt(self, specialization: str) -> str:
        """Get system prompt based on specialization"""
        
        base_prompt = f"""
        Ты — AI-ассистент для эксперта в области {specialization}.
        
        Твоя задача:
        1. Генерировать полезный, вовлекающий контент для социальных сетей (ВКонтакте)
        2. Помогать эксперту отвечать на возражения клиентов
        3. Создавать структуры для марафонов и чек-листы
        
        Важные правила:
        - Ты НЕ ставишь медицинские или психологические диагнозы
        - Ты НЕ даёшь конкретных рекомендаций по лечению
        - Ты НЕ обещаешь гарантированных результатов
        - Ты используешь русский язык, естественно и без шаблонов
        - Всегда предлагай следующий шаг (подписка, консультация, задание)
        
        Для постов используй структуру:
        - Заголовок: цепляющий, интригующий
        - Проблема: что болит у читателя
        - Инсайт: почему это происходит
        - Решение: как эксперт помогает
        - Призыв к действию: лайк, комментарий, переход на консультацию
        """
        
        return base_prompt
    
    async def generate_post(
        self,
        topic: str,
        content_type: str = "post",
        voice_style: Optional[str] = None,
        uniqueness: Optional[str] = None,
        specialization: str = "nutrition",
        include_hashtags: bool = True,
        include_questions: bool = True,
        feedback: Optional[str] = None,
        previous_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a social media post"""
        
        system_prompt = await self._get_system_prompt(specialization)
        
        user_prompt = f"""
        Тема: {topic}
        Тип контента: {content_type}
        """
        
        if voice_style:
            user_prompt += f"\nСтиль общения эксперта: {voice_style}"
        if uniqueness:
            user_prompt += f"\nУникальность эксперта: {uniqueness}"
        if feedback:
            user_prompt += f"\n\nПредыдущая версия поста:\n{previous_version}\n\nОбратная связь: {feedback}\n\nСоздай улучшенную версию с учётом обратной связи."
        
        user_prompt += """
        
        Требования:
        - Длина: 500-1500 знаков с пробелами
        - Язык: русский, естественный, без канцелярита
        - Не используй слова "шок", "секрет", "уникальный", "сенсация"
        
        Ответь в формате JSON:
        {
            "title": "заголовок поста",
            "text": "полный текст поста",
            "hashtags": ["#тег1", "#тег2"] (если нужны),
            "questions": ["вопрос1", "вопрос2"] (для вовлечения)
        }
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            return {
                "text": result.get("text", ""),
                "title": result.get("title", ""),
                "hashtags": result.get("hashtags", []) if include_hashtags else [],
                "questions": result.get("questions", []) if include_questions else [],
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to generate post: {e}")
            return {
                "text": f"Ошибка генерации: {str(e)}",
                "title": topic,
                "hashtags": [],
                "questions": [],
                "tokens_used": 0
            }
    
    async def generate_case_study(
        self,
        problem: str,
        solution: str,
        result: str,
        client_type: Optional[str] = None,
        duration: Optional[str] = None,
        voice_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a case study post"""
        
        system_prompt = """Ты — AI-копирайтер. Твоя задача — превратить сухие факты в продающий кейс.
        
        Структура кейса:
        1. Заголовок: "Кейс: [кратко о результате]"
        2. Проблема клиента (эмпатия)
        3. Что пробовал, но не работало
        4. Как эксперт помог (конкретные шаги)
        5. Результат (цифры, изменения)
        6. Вывод и призыв к действию
        """
        
        user_prompt = f"""
        Проблема клиента: {problem}
        Решение эксперта: {solution}
        Результат: {result}
        """
        
        if client_type:
            user_prompt += f"\nТип клиента: {client_type}"
        if duration:
            user_prompt += f"\nДлительность работы: {duration}"
        if voice_style:
            user_prompt += f"\nСтиль: {voice_style}"
        
        user_prompt += """
        
        Ответь в формате JSON:
        {
            "title": "заголовок кейса",
            "text": "полный текст кейса (800-1500 знаков)",
            "before_after": {"before": "было", "after": "стало"},
            "hashtags": ["#тег1", "#тег2"]
        }
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            return {
                "text": result.get("text", ""),
                "title": result.get("title", ""),
                "before_after": result.get("before_after", {}),
                "hashtags": result.get("hashtags", []),
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to generate case study: {e}")
            return {
                "text": f"Ошибка генерации: {str(e)}",
                "title": "Кейс клиента",
                "before_after": {},
                "hashtags": [],
                "tokens_used": 0
            }
    
    async def generate_reply(
        self,
        message: str,
        voice_style: Optional[str] = None,
        specialization: str = "nutrition"
    ) -> Dict[str, Any]:
        """Generate reply to client message/objection"""
        
        system_prompt = f"""
        Ты — AI-ассистент эксперта в области {specialization}.
        
        Твоя задача: ответить на сообщение потенциального клиента.
        
        Правила:
        - Не обещай мгновенного решения
        - Не ставь диагнозов
        - Не называй конкретных цен (скажи примерный диапазон)
        - Всегда завершай вопросом или призывом к действию
        - Если клиент говорит "дорого" — опиши ценность
        - Если "подумаю" — предложи полезный материал
        """
        
        if voice_style:
            system_prompt += f"\nСтиль общения эксперта: {voice_style}"
        
        user_prompt = f"""
        Сообщение клиента: "{message}"
        
        Ответь в формате JSON:
        {{
            "reply": "текст ответа",
            "strategy": "какая стратегия использована (value, education, empathy, objection_handling)"
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            return {
                "reply": result.get("reply", ""),
                "strategy": result.get("strategy", "value"),
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to generate reply: {e}")
            return {
                "reply": f"Извините, произошла ошибка. Пожалуйста, переформулируйте вопрос.",
                "strategy": "error",
                "tokens_used": 0
            }
    
    async def analyze_comments(self, comments: List[str]) -> Dict[str, Any]:
        """Analyze comments to find common questions and objections"""
        
        if not comments:
            return {"top_questions": [], "top_objections": [], "sentiment": "neutral"}
        
        # Take sample of comments (max 50)
        sample = comments[:50]
        
        user_prompt = f"""
        Проанализируй следующие комментарии подписчиков эксперта по питанию/нутрициологии.
        
        Комментарии:
        {chr(10).join(f'- {c[:200]}' for c in sample)}
        
        Определи:
        1. Топ-3 самых частых вопроса
        2. Топ-3 самых частых возражения ("дорого", "не получится", "нет времени" и т.д.)
        3. Общий настрой (positive, neutral, negative)
        
        Ответь в формате JSON:
        {{
            "top_questions": ["вопрос1", "вопрос2", "вопрос3"],
            "top_objections": ["возражение1", "возражение2", "возражение3"],
            "sentiment": "positive/neutral/negative"
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты — аналитик комментариев в социальных сетях."},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            return {
                "top_questions": result.get("top_questions", []),
                "top_objections": result.get("top_objections", []),
                "sentiment": result.get("sentiment", "neutral")
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze comments: {e}")
            return {"top_questions": [], "top_objections": [], "sentiment": "neutral"}
    
    async def regenerate(
        self,
        original_type: str,
        original_input: str,
        feedback: str,
        previous_version: str
    ) -> Dict[str, Any]:
        """Regenerate content with feedback"""
        
        # Simplified - reuse generate_post logic
        return await self.generate_post(
            topic=original_input,
            content_type=original_type,
            feedback=feedback,
            previous_version=previous_version
        )
