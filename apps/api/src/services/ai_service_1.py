# Добавить в класс AIService следующие методы

async def generate_positioning(
    self,
    specialization: str,
    experience_years: int,
    clients_count: int,
    main_result: str,
    superpower: str,
    target_audience: str,
    values: List[str],
    tone: str
) -> Dict[str, Any]:
    """Generate positioning (УТП) for expert"""
    
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
    - Суперсила (уникальность): {superpower}
    - Целевая аудитория: {target_audience}
    - Ценности: {', '.join(values) if values else 'не указаны'}
    - Желаемый тон: {tone}
    
    Сгенерируй позиционирование в формате JSON:
    {{
        "one_liner": "Одна фраза для шапки профиля (макс 80 символов)",
        "elevator_pitch": "30-секундная презентация для устного знакомства",
        "description": "Развёрнутое описание для страницы «Об эксперте» (200-300 слов)",
        "taglines": ["10 вариантов слоганов для разных ситуаций"],
        "positioning_map": {{
            "all": "что делают все",
            "competitors": "что делают конкуренты (без конкретных имён)",
            "you": "что делаете вы (ваше отличие)"
        }}
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
    audience_connection: str
) -> Dict[str, Any]:
    """Generate personal story"""
    
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
        "story": "Полная история для страницы «Об авторе» (500-800 слов)",
        "short_version": "Короткая версия для закреплённого поста (150-200 слов)",
        "video_script": "Сценарий для видео на 2-3 минуты",
        "key_phrases": ["5 ключевых фраз, которые можно повторять в разных контекстах"]
    }}
    """
    
    return await self._generate_json(system_prompt, user_prompt)


async def analyze_trust_signals(
    self,
    group_info: Dict,
    posts: List[Dict],
    pinned_post: Dict,
    comments: List[Dict]
) -> Dict[str, Any]:
    """Analyze trust signals on VK page"""
    
    system_prompt = """
    Ты — эксперт по доверию и репутации в соцсетях.
    
    Проанализируй страницу ВКонтакте эксперта по следующим критериям:
    1. Визуальное доверие (аватар, обложка, оформление)
    2. Контентное доверие (кейсы, отзывы, экспертные посты)
    3. Социальное доверие (реакции, комментарии, активность)
    4. Экспертное доверие (дипломы, сертификаты, опыт)
    
    Оцени каждый критерий от 0 до 25, дай конкретные замечания.
    """
    
    user_prompt = f"""
    Данные страницы:
    - Название группы: {group_info.get('name')}
    - Описание: {group_info.get('description', '')[:500]}
    - Количество постов: {len(posts)}
    - Количество комментариев в выборке: {len(comments)}
    
    Закреплённый пост: {pinned_post.get('text', 'Нет закреплённого поста')[:300] if pinned_post else 'нет'}
    
    Последние 3 поста (образец):
    {self._format_posts_sample(posts[:3])}
    
    Сгенерируй результат в формате JSON:
    {{
        "overall_score": "общий балл 0-100",
        "scores": {{
            "visual": "балл за визуал 0-25",
            "content": "балл за контент 0-25",
            "social": "балл за социальное доверие 0-25",
            "expertise": "балл за экспертизу 0-25"
        }},
        "issues": ["список проблем (от 5 до 10)"],
        "recommendations": ["список рекомендаций (от 5 до 10)"],
        "quick_wins": [
            {{"action": "действие на 5 минут", "impact": "ожидаемый эффект"}},
            ...
        ]
    }}
    """
    
    return await self._generate_json(system_prompt, user_prompt)


async def analyze_uniqueness(
    self,
    your_info: Dict,
    your_posts: List[Dict],
    competitors: List[Dict]
) -> Dict[str, Any]:
    """Analyze what makes you unique compared to competitors"""
    
    system_prompt = """
    Ты — аналитик рынка и стратег по дифференциации.
    
    Проанализируй эксперта и его конкурентов и найди зону уникальности.
    
    Принципы:
    - Уникальность — это не «я лучше», это «я другой/работаю иначе/решаю другие задачи»
    - Ищи неочевидные отличия в подходе, механике, вовлечении, упаковке
    - Отличай реальную уникальность от «все так говорят»
    """
    
    your_summary = f"""
    Ваша страница:
    - Название: {your_info.get('name')}
    - Описание: {your_info.get('description', '')[:300]}
    """
    
    comp_summary = "\nКонкуренты:\n"
    for i, comp in enumerate(competitors[:3], 1):
        comp_summary += f"{i}. {comp.get('name', 'Неизвестно')}\n"
        comp_summary += f"   Описание: {comp.get('description', '')[:150]}\n"
    
    user_prompt = your_summary + comp_summary + """
    
    Сгенерируй результат в формате JSON:
    {
        "your_positioning": "Как вы позиционируетесь сейчас (по данным страницы)",
        "zone_of_uniqueness": "Зона уникальности — то, что реально отличает вас",
        "common_pitfalls": ["Что делают почти все конкуренты (и вам не стоит повторять)"],
        "differentiators": ["Чем вы уже отличаетесь (если есть)", "Чем могли бы отличаться"],
        "recommended_focus": "На чём стоит фокусироваться в коммуникации"
    }
    """
    
    return await self._generate_json(system_prompt, user_prompt)


async def analyze_voice_style(self, sample_texts: List[str]) -> Dict[str, Any]:
    """Analyze voice style from sample texts"""
    
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
            "persona": "роль/амплуа (эксперт/друг/учитель/мама/наставник)",
            "formality": "formal/professional/casual/friendly",
            "emotional_tone": "заботливый/требовательный/вдохновляющий/ироничный",
            "key_characteristics": ["характеристика1", "характеристика2"]
        }},
        "suggested": {{
            "persona": "рекомендуемая роль",
            "adjustments": ["что изменить", "как изменить"]
        }},
        "phrases_to_use": ["5 примеров фраз, стоит использовать"],
        "phrases_to_avoid": ["5 примеров фраз, стоит избегать"]
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
    special_offer: str,
    deadline: str
) -> Dict[str, Any]:
    """Generate landing page copy"""
    
    user_prompt = f"""
    Создай продающую страницу для услуги:
    - Название услуги: {service_name}
    - Цена: {price} ₽
    - Целевая аудитория: {target_audience}
    - Главная проблема: {main_problem}
    - Решение: {solution}
    - Результаты: {', '.join(results)}
    - Возражения: {', '.join(objections) if objections else 'нет'}
    - Спецпредложение: {special_offer or 'нет'}
    - Дедлайн: {deadline or 'нет'}
    
    Сгенерируй в формате JSON:
    {{
        "title": "заголовок (должен цеплять)",
        "subtitle": "подзаголовок",
        "sections": [
            {{"type": "hero", "content": "..."}},
            {{"type": "problem", "content": "..."}},
            {{"type": "solution", "content": "..."}},
            {{"type": "results", "items": [...]}},
            {{"type": "about_author", "content": "..."}},
            {{"type": "objections", "items": [...]}},
            {{"type": "price", "price": {price}, "special_offer": "{special_offer}"}},
            {{"type": "cta", "text": "..."}}
        ],
        "cta_button_text": "Записаться на консультацию",
        "full_html": "полный HTML код страницы",
        "preview_text": "первые 300 символов для превью"
    }}
    """
    
    return await self._generate_json(self._get_landing_prompt(), user_prompt)


def _format_posts_sample(self, posts: List[Dict]) -> str:
    """Format posts sample for prompt"""
    result = []
    for post in posts[:3]:
        text = post.get('text', '')[:300]
        likes = post.get('likes', {}).get('count', 0)
        comments = post.get('comments', {}).get('count', 0)
        result.append(f"Текст: {text}\nЛайки: {likes}, Комментарии: {comments}\n")
    return "\n---\n".join(result)


def _get_landing_prompt(self) -> str:
    """Get system prompt for landing page generation"""
    return """
    Ты — профессиональный копирайтер, специализирующийся на лендингах для экспертов.
    
    Требования:
    - Текст должен быть на русском
    - Используй заголовки, подзаголовки, списки
    - Добавь блок с ответами на возражения
    - Добавь призыв к действию после каждого блока
    - В HTML используй простые теги: h1, h2, p, ul, li, button
    """
