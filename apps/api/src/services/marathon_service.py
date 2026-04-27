"""
Marathon service - day generation, scheduling, notifications
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from src.models.marathon import MarathonDay

logger = logging.getLogger(__name__)


class MarathonService:
    """Service for marathon management"""
    
    async def generate_days(
        self,
        marathon_id: uuid.UUID,
        structure: List[Dict],
        db: AsyncSession
    ) -> List[MarathonDay]:
        """Generate individual day records from marathon structure"""
        
        days = []
        
        for i, day_data in enumerate(structure, start=1):
            marathon_day = MarathonDay(
                marathon_id=marathon_id,
                day_number=i,
                title=day_data.get("title", f"День {i}"),
                description=day_data.get("description", ""),
                text=day_data.get("text", ""),
                task_title=day_data.get("task", {}).get("title", "Задание дня"),
                task_description=day_data.get("task", {}).get("description", ""),
                task_type=day_data.get("task", {}).get("type", "text"),
                bonus_title=day_data.get("bonus", {}).get("title"),
                bonus_file_url=day_data.get("bonus", {}).get("url"),
                scheduled_for=i - 1,  # days from start
                send_time="10:00"
            )
            db.add(marathon_day)
            days.append(marathon_day)
        
        await db.commit()
        
        # Refresh all days to get ids
        for day in days:
            await db.refresh(day)
        
        logger.info(f"Generated {len(days)} days for marathon {marathon_id}")
        
        return days
    
    async def get_day_content(
        self,
        marathon_id: uuid.UUID,
        day_number: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get content for specific marathon day"""
        
        result = await db.execute(
            select(MarathonDay).where(
                MarathonDay.marathon_id == marathon_id,
                MarathonDay.day_number == day_number
            )
        )
        day = result.scalar_one_or_none()
        
        if not day:
            return {}
        
        return {
            "day_number": day.day_number,
            "title": day.title,
            "description": day.description,
            "text": day.text,
            "video_url": day.video_url,
            "task": {
                "title": day.task_title,
                "description": day.task_description,
                "type": day.task_type
            } if day.task_title else None,
            "bonus": {
                "title": day.bonus_title,
                "file_url": day.bonus_file_url
            } if day.bonus_title else None
        }
    
    async def schedule_daily_messages(
        self,
        marathon_id: uuid.UUID,
        starts_at: datetime,
        days: List[MarathonDay]
    ):
        """Schedule daily messages in queue (Celery tasks)"""
        
        from src.worker.tasks import send_daily_marathon_message
        
        for day in days:
            send_time = starts_at + timedelta(days=day.scheduled_for)
            # Parse time string
            hour, minute = map(int, day.send_time.split(":"))
            send_time = send_time.replace(hour=hour, minute=minute)
            
            # Schedule Celery task
            send_daily_marathon_message.apply_async(
                args=[str(marathon_id), day.day_number],
                eta=send_time
            )
        
        logger.info(f"Scheduled daily messages for marathon {marathon_id}")
