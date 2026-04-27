"""
AI Service - integration with LLMs (OpenAI)
"""

import json
import logging
from typing import Optional, Dict, Any, List

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
        logger.info("AI Service initialized")

    async def shutdown(self):
        await self.client.close()
        logger.info("AI Service shutdown")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Call the chat completion API expecting a JSON object response."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature if temperature is None else temperature,
                max_tokens=self.max_tokens if max_tokens is None else max_tokens,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            data = json.loads(content)
            if response.usage:
                data.setdefault("_tokens_used", response.usage.total_tokens)
            return data
        except Exception as e:
            logger.exception("OpenAI request failed: %s", e)
            return {"error": str(e)}

    @staticmethod
    def _format_posts_sample(posts: List[Dict]) -> str:
        result = []
        for post in posts[:3]:
            text = (post.get("text") or "")[:300]
            likes = post.get("likes", {}).get("count", 0)
            comments = post.get("comments", {}).get("count", 0)
            result.append(f"Текст: {text}\nЛайки: {likes}, Комментарии: {comments}\n")
        return "\n---\n".join(result)

    async def _get_system_prompt(self, specialization: str) -> str:
        return f"""
        Ты — AI-ассистент для эксперта в области {specialization}.

        Твоя задача:
        1. Генерировать полезный, вовлекающий контент для социальных сетей (ВКонтакте)
        2. Помогать эксперту отвечать на возражения клиентов
        3. Создавать структуры для марафонов и чек-листы

        Важные правила:
        - Ты НЕ ставишь медицинские или психологические диагнозы
        - Ты НЕ даёшь конкретных рекомендаций по лечению
        - Ты НЕ обещаешь гарантированных результатов
        - Используй русский язык, естественно и без шаблонов
        - Всегда предлагай следующий шаг (подписка, консультация, задание)
        """

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------

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
        previous_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        system_prompt = await self._get_system_prompt(specialization)

        user_prompt = f"Тема: {topic}\nТип контента: {content_type}"
        if voice_style:
            user_prompt += f"\nСтиль общения эксперта: {voice_style}"
        if uniqueness:
            user_prompt += f"\nУникальность эксперта: {uniqueness}"
        if feedback:
            user_prompt += (
                f"\n\nПредыдущая версия поста:\n{previous_version}\n\n"
                f"Обратная связь: {feedback}\n\n"
                "Создай улучшенную версию с учётом обратной связи."
            )
        user_prompt += """

        Требования:
        - Длина: 500-1500 знаков с пробелами
        - Язык: русский, естественный, без канцелярита
        - Не используй слова "шок", "секрет", "уникальный", "сенсация"

        Ответь в формате JSON:
        {
            "title": "заголовок поста",
            "text": "полный текст поста",
            "hashtags": ["#тег1", "#тег2"],
            "questions": ["вопрос1", "вопрос2"]
        }
        """

        result = await self._generate_json(system_prompt, user_prompt)
        return {
            "text": result.get("text", ""),
            "title": result.get("title", topic),
            "hashtags": result.get("hashtags", []) if include_hashtags else [],
            "questions": result.get("questions", []) if include_questions else [],
            "tokens_used": result.get("_tokens_used", 0),
        }

    async def generate_case_study(
        self,
        problem: str,
        solution: str,
        result: str,
        client_type: Optional[str] = None,
        duration: Optional[str] = None,
        voice_style: Optional[str] = None,
    ) -> Dict[str, Any]:
        system_prompt = """Ты — AI-копирайтер. Твоя задача — превратить сухие факты в продающий кейс.

        Структура кейса:
        1. Заголовок: "Кейс: [кратко о результате]"
        2. Проблема клиента (эмпатия)
        3. Что пробовал, но не работало
        4. Как эксперт помог (конкретные шаги)
        5. Результат (цифры, изменения)
        6. Вывод и призыв к действию
        """

        user_prompt = (
            f"Проблема клиента: {problem}\n"
            f"Решение эксперта: {solution}\n"
            f"Результат: {result}\n"
        )
        if client_type:
            user_prompt += f"Тип клиента: {client_type}\n"
        if duration:
            user_prompt += f"Длительность работы: {duration}\n"
        if voice_style:
            user_prompt += f"Стиль: {voice_style}\n"

        user_prompt += """

        Ответь в формате JSON:
        {
            "title": "заголовок кейса",
            "text": "полный текст кейса (800-1500 знаков)",
            "before_after": {"before": "было", "after": "стало"},
            "hashtags": ["#тег1", "#тег2"]
        }
        """

        data = await self._generate_json(system_prompt, user_prompt)
        return {
            "text": data.get("text", ""),
            "title": data.get("title", "Кейс клиента"),
            "before_after": data.get("before_after", {}),
            "hashtags": data.get("hashtags", []),
            "tokens_used": data.get("_tokens_used", 0),
        }

    async def generate_reply(
        self,
        message: str,
        voice_style: Optional[str] = None,
        specialization: str = "nutrition",
    ) -> Dict[str, Any]:
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
            "strategy": "value|education|empathy|objection_handling"
        }}
        """

        data = await self._generate_json(
            system_prompt, user_prompt, temperature=0.7, max_tokens=500
        )
        return {
            "reply": data.get("reply", ""),
            "strategy": data.get("strategy", "value"),
            "tokens_used": data.get("_tokens_used", 0),
        }

    async def analyze_comments(self, comments: List[str]) -> Dict[str, Any]:
        if not comments:
            return {"top_questions": [], "top_objections": [], "sentiment": "neutral"}

        sample = comments[:50]
        user_prompt = f"""
        Проанализируй следующие комментарии подписчиков эксперта.

        Комментарии:
        {chr(10).join(f'- {c[:200]}' for c in sample)}

        Определи:
        1. Топ-3 самых частых вопроса
        2. Топ-3 самых частых возражения
        3. Общий настрой (positive, neutral, negative)

        Ответь в формате JSON:
        {{
            "top_questions": ["вопрос1", "вопрос2", "вопрос3"],
            "top_objections": ["возражение1", "возражение2", "возражение3"],
            "sentiment": "positive|neutral|negative"
        }}
        """

        data = await self._generate_json(
            "Ты — аналитик комментариев в социальных сетях.",
            user_prompt,
            temperature=0.3,
            max_tokens=500,
        )
        return {
            "top_questions": data.get("top_questions", []),
            "top_objections": data.get("top_objections", []),
            "sentiment": data.get("sentiment", "neutral"),
        }

    async def regenerate(
        self,
        original_type: str,
        original_input: str,
        feedback: str,
        previous_version: str,
    ) -> Dict[str, Any]:
        return await self.generate_post(
            topic=original_input,
            content_type=original_type,
            feedback=feedback,
            previous_version=previous_version,
        )

    # ------------------------------------------------------------------
    # Brand / Positioning
    # ------------------------------------------------------------------

    async def generate_positioning(
        self,
        specialization: str,
        experience_years: int,
        clients_count: int,
        main_result: str,
        superpower: str,
        target_audience: str,
        values: List[str],
        tone: str,
    ) -> Dict[str, Any]:
        system_prompt = f"""
        Ты — эксперт по маркетингу и позиционированию для профессионалов.

        Помоги эксперту в области {specialization} сформулировать чёткое позиционирование.

        Критерии хорошего позиционирования:
        - Понятно, для кого
        - Понятно, от какой проблемы
        - Понятно, какой результат
        - Отличимость от других
        - Помещается в одно предложение
        """

        user_prompt = f"""
        Данные эксперта:
        - Специализация: {specialization}
        - Опыт: {experience_years} лет
        - Клиентов: {clients_count}
        - Главный результат клиентов: {main_result}
        - Суперсила: {superpower}
        - Целевая аудитория: {target_audience}
        - Ценности: {', '.join(values) if values else 'не указаны'}
        - Желаемый тон: {tone}

        Сгенерируй позиционирование в формате JSON:
        {{
            "one_liner": "Одна фраза для шапки профиля (макс 80 символов)",
            "elevator_pitch": "30-секундная презентация",
            "description": "Развёрнутое описание (200-300 слов)",
            "taglines": ["10 вариантов слоганов"],
            "positioning_map": {{
                "all": "что делают все",
                "competitors": "что делают конкуренты",
                "you": "ваше отличие"
            }}
        }}
        """

        return await self._generate_json(system_prompt, user_prompt)

    async def analyze_current_positioning(
        self,
        group_info: Dict[str, Any],
        posts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Infer current positioning from a VK group page and recent posts."""
        system_prompt = """
        Ты — эксперт по позиционированию. По описанию страницы и постам определи,
        как эксперт сейчас позиционирует себя и что можно улучшить.
        """

        user_prompt = f"""
        Название группы: {group_info.get('name', '')}
        Описание: {(group_info.get('description') or '')[:500]}

        Примеры постов:
        {self._format_posts_sample(posts)}

        Ответь в формате JSON:
        {{
            "one_liner": "одна фраза, как вы сейчас позиционируетесь",
            "strengths": ["сильные стороны"],
            "weaknesses": ["что мешает"],
            "improvements": ["что улучшить"]
        }}
        """

        return await self._generate_json(system_prompt, user_prompt)

    async def generate_personal_story(
        self,
        background: str,
        turning_point: str,
        learning: str,
        results: str,
        mission: str,
        audience_connection: str,
    ) -> Dict[str, Any]:
        system_prompt = """
        Ты — сторителлинг-эксперт. Помоги эксперту написать личную историю.

        Правила хорошей истории:
        - Эмоциональная вовлечённость
        - Конкретные детали (не абстракции)
        - Понятная арка: было → понял → изменился → помогает другим
        - Связь с аудиторией
        - Призыв к действию в конце
        """

        user_prompt = f"""
        Данные эксперта:
        - Предыстория: {background}
        - Точка перелома: {turning_point}
        - Чему научился: {learning}
        - Результаты: {results}
        - Миссия: {mission}
        - Связь с аудиторией: {audience_connection}

        Сгенерируй историю в формате JSON:
        {{
            "story": "Полная история (500-800 слов)",
            "short_version": "Короткая версия (150-200 слов)",
            "video_script": "Сценарий для видео на 2-3 минуты",
            "key_phrases": ["5 ключевых фраз"]
        }}
        """

        return await self._generate_json(system_prompt, user_prompt)

    async def analyze_trust_signals(
        self,
        group_info: Dict[str, Any],
        posts: List[Dict[str, Any]],
        pinned_post: Optional[Dict[str, Any]],
        comments: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        system_prompt = """
        Ты — эксперт по доверию и репутации в соцсетях.

        Проанализируй страницу ВКонтакте по критериям:
        1. Визуальное доверие (аватар, обложка, оформление)
        2. Контентное доверие (кейсы, отзывы, экспертные посты)
        3. Социальное доверие (реакции, комментарии, активность)
        4. Экспертное доверие (дипломы, сертификаты, опыт)

        Оцени каждый критерий от 0 до 25.
        """

        pinned_text = (pinned_post.get("text") if pinned_post else "") or "нет"
        user_prompt = f"""
        Данные страницы:
        - Название: {group_info.get('name')}
        - Описание: {(group_info.get('description') or '')[:500]}
        - Постов: {len(posts)}
        - Комментариев: {len(comments)}

        Закреплённый пост: {pinned_text[:300]}

        Образец постов:
        {self._format_posts_sample(posts[:3])}

        Сгенерируй результат в формате JSON:
        {{
            "overall_score": 0,
            "scores": {{"visual": 0, "content": 0, "social": 0, "expertise": 0}},
            "issues": ["..."],
            "recommendations": ["..."],
            "quick_wins": [{{"action": "...", "impact": "..."}}]
        }}
        """

        return await self._generate_json(system_prompt, user_prompt)

    async def analyze_uniqueness(
        self,
        your_info: Dict[str, Any],
        your_posts: List[Dict[str, Any]],
        competitors: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        system_prompt = """
        Ты — аналитик рынка и стратег по дифференциации.

        Найди реальную зону уникальности эксперта по сравнению с конкурентами.
        Уникальность — это не «я лучше», это «я другой».
        """

        your_summary = (
            f"Ваша страница:\n"
            f"- Название: {your_info.get('name')}\n"
            f"- Описание: {(your_info.get('description') or '')[:300]}\n"
        )

        comp_summary = "\nКонкуренты:\n"
        for i, comp in enumerate(competitors[:3], 1):
            comp_summary += f"{i}. {comp.get('name', 'Неизвестно')}\n"
            comp_summary += f"   Описание: {(comp.get('description') or '')[:150]}\n"

        user_prompt = your_summary + comp_summary + """

        Сгенерируй результат в формате JSON:
        {
            "your_positioning": "Как вы позиционируетесь сейчас",
            "zone_of_uniqueness": "Зона уникальности",
            "common_pitfalls": ["Что делают почти все"],
            "differentiators": ["Чем вы отличаетесь"],
            "recommended_focus": "На чём фокусироваться"
        }
        """

        return await self._generate_json(system_prompt, user_prompt)

    async def analyze_voice_style(self, sample_texts: List[str]) -> Dict[str, Any]:
        samples = "\n---\n".join(sample_texts[:10])

        system_prompt = """
        Ты — эксперт по тональности и стилю коммуникации.
        Проанализируй тексты и определи текущий голос эксперта.
        """

        user_prompt = f"""
        Образцы текстов:

        {samples}

        Сгенерируй результат в формате JSON:
        {{
            "current": {{
                "persona": "роль/амплуа",
                "formality": "formal|professional|casual|friendly",
                "emotional_tone": "...",
                "key_characteristics": ["..."]
            }},
            "suggested": {{
                "persona": "рекомендуемая роль",
                "adjustments": ["..."]
            }},
            "phrases_to_use": ["..."],
            "phrases_to_avoid": ["..."]
        }}
        """

        return await self._generate_json(system_prompt, user_prompt)

    async def generate_landing_page(
        self,
        service_name: str,
        price: float,
        target_audience: str,
        main_problem: str,
        solution: str,
        results: List[str],
        objections: List[str],
        special_offer: Optional[str],
        deadline: Optional[str],
    ) -> Dict[str, Any]:
        system_prompt = """
        Ты — профессиональный копирайтер, специализирующийся на лендингах для экспертов.

        Требования:
        - Текст на русском
        - Используй заголовки, подзаголовки, списки
        - Добавь блок с ответами на возражения
        - Призыв к действию после каждого блока
        - HTML — простые теги: h1, h2, p, ul, li, button
        """

        user_prompt = f"""
        Создай продающую страницу для услуги:
        - Название: {service_name}
        - Цена: {price} ₽
        - Целевая аудитория: {target_audience}
        - Проблема: {main_problem}
        - Решение: {solution}
        - Результаты: {', '.join(results)}
        - Возражения: {', '.join(objections) if objections else 'нет'}
        - Спецпредложение: {special_offer or 'нет'}
        - Дедлайн: {deadline or 'нет'}

        Ответь в формате JSON:
        {{
            "title": "заголовок",
            "subtitle": "подзаголовок",
            "sections": [
                {{"type": "hero", "content": "..."}},
                {{"type": "problem", "content": "..."}},
                {{"type": "solution", "content": "..."}},
                {{"type": "results", "items": []}},
                {{"type": "about_author", "content": "..."}},
                {{"type": "objections", "items": []}},
                {{"type": "price", "price": {price}, "special_offer": "{special_offer or ''}"}},
                {{"type": "cta", "text": "..."}}
            ],
            "cta_button_text": "Записаться на консультацию",
            "full_html": "полный HTML код страницы",
            "preview_text": "первые 300 символов"
        }}
        """

        return await self._generate_json(system_prompt, user_prompt)
