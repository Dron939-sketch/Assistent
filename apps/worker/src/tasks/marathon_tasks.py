"""
Background tasks for marathons
"""

from celery import shared_task
import logging
from datetime import datetime, timedelta, timezone
import uuid

from src.services.telegram_service import TelegramService
from src.services.vk_service import VKService
from src.database import get_db_session

logger = logging.getLogger(__name__)


@shared_task(name="src.tasks.marathon_tasks.send_daily_marathon_message")
def send_daily_marathon_message(marathon_id: str, day_number: int):
    """
    Send daily message to all active marathon participants
    """
    logger.info(f"Sending day {day_number} for marathon {marathon_id}")
    
    session = get_db_session()
    
    try:
        from src.models.marathon import Marathon, MarathonParticipant, MarathonDay
        
        marathon = session.query(Marathon).filter(Marathon.id == uuid.UUID(marathon_id)).first()
        if not marathon or marathon.status != "active":
            logger.warning(f"Marathon {marathon_id} not active")
            return
        
        day = session.query(MarathonDay).filter(
            MarathonDay.marathon_id == marathon.id,
            MarathonDay.day_number == day_number
        ).first()
        
        if not day:
            logger.error(f"Day {day_number} not found for marathon {marathon_id}")
            return
        
        # Get active participants
        participants = session.query(MarathonParticipant).filter(
            MarathonParticipant.marathon_id == marathon.id,
            MarathonParticipant.status == "active"
        ).all()
        
        # Build message
        message = f"📅 День {day_number}: {day.title}\n\n"
        message += day.text or day.description or ""
        
        if day.task_title:
            message += f"\n\n📝 Задание: {day.task_title}\n{day.task_description or ''}"
        
        if day.bonus_title:
            message += f"\n\n🎁 Бонус: {day.bonus_title}"
        
        # Send to each participant
        for participant in participants:
            try:
                if marathon.platform == "telegram":
                    tg_service = TelegramService()
                    # Async call in sync context
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        tg_service.send_message(
                            chat_id=participant.contact,
                            text=message
                        )
                    )
                    loop.close()
                else:
                    # VK
                    vk_service = VKService()
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        vk_service.send_message(
                            peer_id=int(participant.contact),
                            message=message
                        )
                    )
                    loop.close()
                
                participant.messages_sent += 1
                
                # Update last active
                participant.last_active_at = datetime.now(timezone.utc)
                
            except Exception as e:
                logger.error(f"Failed to send to {participant.contact}: {e}")
        
        session.commit()
        logger.info(f"Sent day {day_number} to {len(participants)} participants")
        
    except Exception as e:
        logger.error(f"Failed to send marathon day {day_number}: {e}")
        raise
    finally:
        session.close()


@shared_task(name="src.tasks.marathon_tasks.check_homework")
def check_homework(submission_id: str):
    """
    Check homework submission using AI (async)
    """
    logger.info(f"Checking homework submission {submission_id}")
    
    session = get_db_session()
    
    try:
        from src.models.marathon import MarathonParticipant
        from src.services.ai_service import AIService
        
        # Get submission data (simplified - would need a HomeworkSubmission model)
        # For now, assume data is passed in
        
        # AI check
        ai_service = AIService()
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            ai_service.check_homework(
                task="Sample task",
                submission="Sample submission",
                marathon_theme="Nutrition"
            )
        )
        loop.close()
        
        logger.info(f"Homework {submission_id} score: {result.get('score')}")
        
    except Exception as e:
        logger.error(f"Failed to check homework {submission_id}: {e}")
        raise
    finally:
        session.close()


@shared_task(name="src.tasks.marathon_tasks.process_daily_marathon_sends")
def process_daily_marathon_sends():
    """
    Process all daily sends for active marathons
    Called every 5 minutes by beat
    """
    logger.info("Processing daily marathon sends")
    
    session = get_db_session()
    
    try:
        from src.models.marathon import Marathon, MarathonDay
        
        now = datetime.now(timezone.utc)
        
        # Get active marathons
        marathons = session.query(Marathon).filter(
            Marathon.status == "active",
            Marathon.starts_at <= now,
            Marathon.ends_at >= now
        ).all()
        
        for marathon in marathons:
            # Calculate which day should be sent
            days_since_start = (now - marathon.starts_at).days
            current_day = days_since_start + 1  # day 1 is start day
            
            if current_day < 1 or current_day > marathon.duration_days:
                continue
            
            # Check if already sent today
            day = session.query(MarathonDay).filter(
                MarathonDay.marathon_id == marathon.id,
                MarathonDay.day_number == current_day
            ).first()
            
            if day and day.sent_at is None:
                # Send
                send_daily_marathon_message.delay(str(marathon.id), current_day)
                day.sent_at = now
                session.commit()
        
        logger.info(f"Processed {len(marathons)} marathons")
        
    except Exception as e:
        logger.error(f"Failed to process daily sends: {e}")
    finally:
        session.close()


@shared_task(name="src.tasks.marathon_tasks.send_reminder")
def send_marathon_reminder(participant_id: str, marathon_id: str, day_number: int):
    """
    Send reminder to participant who hasn't completed the day
    """
    logger.info(f"Sending reminder to participant {participant_id} for day {day_number}")
    
    session = get_db_session()
    
    try:
        from src.models.marathon import Marathon, MarathonParticipant
        
        participant = session.query(MarathonParticipant).filter(
            MarathonParticipant.id == uuid.UUID(participant_id)
        ).first()
        
        marathon = session.query(Marathon).filter(Marathon.id == uuid.UUID(marathon_id)).first()
        
        if not participant or not marathon:
            return
        
        reminder_text = f"Напоминание: вы ещё не завершили день {day_number} марафона «{marathon.name}». Не откладывайте!"
        
        if marathon.platform == "telegram":
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tg_service = TelegramService()
            loop.run_until_complete(
                tg_service.send_message(
                    chat_id=participant.contact,
                    text=reminder_text
                )
            )
            loop.close()
        
        logger.info(f"Reminder sent to {participant.contact}")
        
    except Exception as e:
        logger.error(f"Failed to send reminder: {e}")
    finally:
        session.close()
