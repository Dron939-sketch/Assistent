"""
VK Audit service - analyzes VK page and generates recommendations
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from src.services.vk_service import VKService
from src.services.ai_service import AIService

logger = logging.getLogger(__name__)


class AuditService:
    """Service for auditing VK pages"""
    
    def __init__(self):
        self.vk_service = VKService()
        self.ai_service = AIService()
    
    async def audit_vk_page(self, group_id: str, user_id: str) -> Dict[str, Any]:
        """
        Perform full audit of VK page
        Returns structured audit results with scores and recommendations
        """
        
        # Fetch data
        group_info = await self.vk_service.get_group_info(group_id)
        posts = await self.vk_service.get_wall_posts(group_id, count=20)
        pinned_post = await self.vk_service.get_pinned_post(group_id)
        
        # Collect comments from last 5 posts for analysis
        comments = []
        for post in posts[:5]:
            post_comments = await self.vk_service.get_post_comments(
                group_id, 
                post.get("id", 0),
                count=50
            )
            comments.extend(post_comments)
        
        # Analyze each category
        categories = []
        
        # 1. Cover analysis
        categories.append(await self._analyze_cover(group_info))
        
        # 2. Avatar analysis
        categories.append(await self._analyze_avatar(group_info))
        
        # 3. Pinned post analysis
        categories.append(await self._analyze_pinned_post(pinned_post))
        
        # 4. Description / about section
        categories.append(await self._analyze_description(group_info))
        
        # 5. Content quality analysis
        categories.append(await self._analyze_content(posts))
        
        # 6. Engagement analysis
        categories.append(await self._analyze_engagement(posts))
        
        # 7. Comments analysis (top questions/objections)
        categories.append(await self._analyze_comments(comments))
        
        # 8. Post diversity (content types)
        categories.append(await self._analyze_post_diversity(posts))
        
        # 9. Consistency (posting frequency)
        categories.append(await self._analyze_consistency(posts))
        
        # 10. Trust signals
        categories.append(await self._analyze_trust_signals(group_info, posts))
        
        # Generate global recommendations using AI
        global_recommendations = await self._generate_recommendations(categories, group_info)
        
        return {
            "categories": categories,
            "global_recommendations": global_recommendations,
            "group_info": group_info,
            "audited_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def _analyze_cover(self, group_info: Dict) -> Dict[str, Any]:
        """Analyze group cover image"""
        cover = group_info.get("cover", {})
        
        issues = []
        recommendations = []
        score = 0
        max_score = 10
        
        # Check if cover exists
        if not cover:
            issues.append("Отсутствует обложка сообщества")
            recommendations.append("Добавьте обложку с вашим фото и УТП")
            score = 0
        else:
            score += 5
            # TODO: Check if cover has text, quality, etc.
        
        return {
            "category": "Обложка",
            "score": score,
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _analyze_avatar(self, group_info: Dict) -> Dict[str, Any]:
        """Analyze group avatar"""
        photo = group_info.get("photo_200", "")
        
        issues = []
        recommendations = []
        score = 0
        max_score = 10
        
        if not photo:
            issues.append("Отсутствует аватар сообщества")
            recommendations.append("Загрузите чёткое фото. Лучше всего — ваше лицо, а не логотип")
            score = 0
        else:
            score += 5
            recommendations.append("Аватар есть, но проверьте, хорошо ли он виден в уменьшенном виде")
        
        return {
            "category": "Аватар",
            "score": score,
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _analyze_pinned_post(self, pinned_post: Optional[Dict]) -> Dict[str, Any]:
        """Analyze pinned post"""
        issues = []
        recommendations = []
        score = 0
        max_score = 10
        
        if not pinned_post:
            issues.append("Нет закреплённого поста")
            recommendations.append("Закрепите пост, который приветствует новых подписчиков и ведёт к действию")
            score = 0
        else:
            text = pinned_post.get("text", "")
            score += 3
            
            if "консультац" not in text.lower() and "запись" not in text.lower():
                issues.append("В закреплённом посте нет призыва к действию (запись, консультация)")
                recommendations.append("Добавьте в закреплённый пост ссылку на запись или бесплатный гайд")
                score = 0
            else:
                score += 4
            
            if len(text) < 100:
                issues.append("Закреплённый пост слишком короткий")
                recommendations.append("Расскажите в закрепе о себе, своих услугах и как записаться")
                score = 0
        
        return {
            "category": "Закреп",
            "score": score,
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _analyze_description(self, group_info: Dict) -> Dict[str, Any]:
        """Analyze group description"""
        description = group_info.get("description", "")
        
        issues = []
        recommendations = []
        score = 0
        max_score = 10
        
        if not description or len(description) < 50:
            issues.append("Описание сообщества слишком короткое или отсутствует")
            recommendations.append("Напишите развёрнутое описание: кто вы, кому помогаете, как записаться")
            score = 0
        else:
            score += 5
            
            if "нутрициолог" not in description.lower() and "эксперт" not in description.lower():
                issues.append("В описании не указана ваша специализация")
                recommendations.append("Чётко укажите, кто вы: нутрициолог, эксперт по питанию и т.д.")
                score = 0
            else:
                score += 3
        
        return {
            "category": "Описание",
            "score": score,
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _analyze_content(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze content quality"""
        issues = []
        recommendations = []
        score = 0
        max_score = 15
        
        if not posts:
            issues.append("На стене нет постов")
            recommendations.append("Начните регулярно публиковать полезный контент")
            score = 0
        else:
            # Count posts with value (longer than 200 chars)
            valuable_posts = sum(1 for p in posts if len(p.get("text", "")) > 200)
            valuable_ratio = valuable_posts / len(posts) if posts else 0
            
            if valuable_ratio < 0.5:
                issues.append("Большинство постов — короткие или не несут ценности")
                recommendations.append("Пишите более развёрнутые посты с конкретной пользой для подписчика")
                score = 5
            else:
                score = 10
            
            # Check for case studies
            case_keywords = ["кейс", "результат", "клиент", "до/после", "похудел", "сбросил"]
            has_cases = any(any(kw in p.get("text", "").lower() for kw in case_keywords) for p in posts)
            
            if not has_cases:
                issues.append("Нет постов с кейсами клиентов")
                recommendations.append("Регулярно публикуйте кейсы: проблема → решение → результат")
                score += 0
            else:
                score += 5
        
        return {
            "category": "Контент",
            "score": min(score, max_score),
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _analyze_engagement(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze post engagement"""
        issues = []
        recommendations = []
        score = 0
        max_score = 15
        
        if not posts:
            score = 0
        else:
            total_likes = sum(p.get("likes", {}).get("count", 0) for p in posts)
            total_comments = sum(p.get("comments", {}).get("count", 0) for p in posts)
            total_reposts = sum(p.get("reposts", {}).get("count", 0) for p in posts)
            
            avg_likes = total_likes / len(posts) if posts else 0
            avg_comments = total_comments / len(posts) if posts else 0
            
            if avg_likes < 20:
                issues.append(f"Низкий охват и вовлечение (в среднем {int(avg_likes)} лайков на пост)")
                recommendations.append("Работайте над качеством контента. Добавьте вопросы в конце постов")
                score = 5
            elif avg_likes < 50:
                score = 10
            else:
                score = 15
            
            if avg_comments < 2:
                issues.append("Подписчики почти не комментируют посты")
                recommendations.append("Задавайте вопросы в конце постов, чтобы стимулировать обсуждение")
                score = max(0, score - 5)
        
        return {
            "category": "Вовлечение",
            "score": score,
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _analyze_comments(self, comments: List[Dict]) -> Dict[str, Any]:
        """Analyze comments to find common questions/objections"""
        issues = []
        recommendations = []
        score = 0
        max_score = 10
        
        if not comments:
            issues.append("Нет комментариев для анализа")
            recommendations.append("Стимулируйте комментарии, чтобы понимать боли аудитории")
            score = 0
        else:
            comment_texts = [c.get("text", "") for c in comments if c.get("text")]
            
            # Use AI to analyze comment patterns
            analysis = await self.ai_service.analyze_comments(comment_texts)
            
            top_questions = analysis.get("top_questions", [])
            top_objections = analysis.get("top_objections", [])
            
            if top_questions:
                recommendations.append(f"Самые частые вопросы: {', '.join(top_questions[:3])}. Напишите посты-ответы на них")
                score += 5
            
            if top_objections:
                recommendations.append(f"Частые возражения: {', '.join(top_objections[:2])}. Добавьте блок с ответами на возражения в описание")
                score += 5
        
        return {
            "category": "Комментарии",
            "score": min(score, max_score),
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _analyze_post_diversity(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze content type diversity"""
        issues = []
        recommendations = []
        max_score = 10
        diversity_count = 0
        score = 0

        if posts:
            has_text = False
            has_image = False
            has_video = False
            has_quiz = False

            for post in posts:
                text = post.get("text", "")
                attachments = post.get("attachments", [])

                if len(text) > 200:
                    has_text = True
                for att in attachments:
                    att_type = att.get("type")
                    if att_type == "photo":
                        has_image = True
                    elif att_type == "video":
                        has_video = True

                if "? " in text or "опрос" in text.lower() or "выберите" in text.lower():
                    has_quiz = True

            diversity_count = sum([has_text, has_image, has_video, has_quiz])
            score = diversity_count * 2

        if diversity_count < 3:
            issues.append("Однообразие форматов постов")
            recommendations.append("Чередуйте форматы: полезные посты, видео, опросы, кейсы")
        
        return {
            "category": "Разнообразие",
            "score": min(score, max_score),
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _analyze_consistency(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze posting consistency"""
        issues = []
        recommendations = []
        score = 0
        max_score = 10
        
        if len(posts) < 8:
            issues.append(f"Всего {len(posts)} постов за последнее время")
            recommendations.append("Публикуйте минимум 3–4 поста в неделю для поддержания активности")
            score = 0
        elif len(posts) < 15:
            score = 5
        else:
            score = 10
        
        return {
            "category": "Регулярность",
            "score": score,
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _analyze_trust_signals(self, group_info: Dict, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze trust signals on page"""
        issues = []
        recommendations = []
        score = 0
        max_score = 10
        
        # Check for contact info
        description = group_info.get("description", "")
        if "http" not in description and "@" not in description:
            issues.append("Нет ссылок на контакты (Telegram, WhatsApp)")
            recommendations.append("Добавьте ссылки на контакты в описание сообщества")
        else:
            score += 3
        
        # Check for reviews/testimonials
        reviews_found = any("отзыв" in p.get("text", "").lower() for p in posts)
        if not reviews_found:
            issues.append("Нет постов с отзывами клиентов")
            recommendations.append("Собирайте и публикуйте отзывы — это повышает доверие")
        else:
            score += 4
        
        return {
            "category": "Доверие",
            "score": min(score, max_score),
            "max_score": max_score,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _generate_recommendations(
        self, 
        categories: List[Dict], 
        group_info: Optional[Dict]
    ) -> Dict[str, Any]:
        """Generate prioritized global recommendations using AI"""
        
        # Collect all recommendations with their categories
        all_recs = []
        for cat in categories:
            for rec in cat.get("recommendations", []):
                all_recs.append({
                    "category": cat["category"],
                    "recommendation": rec,
                    "priority": "high" if cat.get("score", 0) < cat.get("max_score", 10) * 0.3 else "medium"
                })
        
        # Prioritize
        high_priority = [r for r in all_recs if r["priority"] == "high"]
        medium_priority = [r for r in all_recs if r["priority"] == "medium"]
        
        # Select top 3-5 most impactful
        top_recs = high_priority[:3] + medium_priority[:2]
        
        return {
            "summary": f"Ваша страница набрала {sum(c.get('score', 0) for c in categories)} из {sum(c.get('max_score', 0) for c in categories)} баллов",
            "priority_actions": [
                {"action": r["recommendation"], "category": r["category"]} 
                for r in top_recs
            ],
            "quick_wins": top_recs[:2]
        }
