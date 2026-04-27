"""
Background tasks for notifications
"""

from celery import shared_task
import logging
from datetime import datetime, timedelta
import uuid

from src.database import get_db_session

logger = logging.getLogger(__name__)


@shared_task(name="src.tasks.notification_tasks.send_telegram_notification")
def send_telegram_notification(chat_id: str, message: str):
    """
    Send notification via Telegram
    """
    logger.info(f"Sending Telegram notification to {chat_id}")
    
    from src.services.telegram_service import TelegramService
    
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        tg_service = TelegramService()
        loop.run_until_complete(
            tg_service.send_message(chat_id=chat_id, text=message)
        )
        loop.close()
        
        logger.info(f"Telegram notification sent to {chat_id}")
        
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")


@shared_task(name="src.tasks.notification_tasks.send_email")
def send_email(to_email: str, subject: str, body: str):
    """
    Send email notification
    """
    logger.info(f"Sending email to {to_email}")
    
    # Implement with SMTP
    # For now, just log
    logger.info(f"Email would be sent: {subject}")


@shared_task(name="src.tasks.notification_tasks.check_expired_subscriptions")
def check_expired_subscriptions():
    """
    Check for expired subscriptions and notify users
    """
    logger.info("Checking expired subscriptions")
    
    session = get_db_session()
    
    try:
        from src.models.user import User
        
        now = datetime.utcnow()
        
        # Find expired subscriptions
        expired = session.query(User).filter(
            User.subscription_status == "active",
            User.subscription_expires_at < now
        ).all()
        
        for user in expired:
            user.subscription_status = "expired"
            
            # Send notification
            send_telegram_notification.delay(
                chat_id=user.telegram_chat_id,
                message=f"⚠️ Ваша подписка FishFlow истекла. Продлите, чтобы продолжить пользоваться сервисом. {user.current_tier}"
            )
            
            logger.info(f"User {user.email} subscription expired")
        
        session.commit()
        logger.info(f"Found {len(expired)} expired subscriptions")
        
        # Find upcoming expirations (7 days)
        upcoming = session.query(User).filter(
            User.subscription_status == "active",
            User.subscription_expires_at.between(now, now + timedelta(days=7))
        ).all()
        
        for user in upcoming:
            days_left = (user.subscription_expires_at - now).days
            send_telegram_notification.delay(
                chat_id=user.telegram_chat_id,
                message=f"📅 Через {days_left} дней истекает ваша подписка FishFlow. Пожалуйста, продлите её."
            )
        
        logger.info(f"Notified {len(upcoming)} users about upcoming expiration")
        
    except Exception as e:
        logger.error(f"Failed to check expired subscriptions: {e}")
    finally:
        session.close()


@shared_task(name="src.tasks.notification_tasks.send_new_lead_notification")
def send_new_lead_notification(user_id: str, lead_data: dict):
    """
    Send notification to expert about new lead
    """
    logger.info(f"Sending new lead notification to user {user_id}")
    
    session = get_db_session()
    
    try:
        from src.models.user import User
        
        user = session.query(User).filter(User.id == uuid.UUID(user_id)).first()
        
        if user and user.telegram_chat_id:
            message = f"🆕 Новый лид!\n\n"
            message += f"Имя: {lead_data.get('name', 'Не указано')}\n"
            message += f"Контакт: {lead_data.get('contact', 'Не указан')}\n"
            message += f"Источник: {lead_data.get('source', 'Unknown')}\n"
            message += f"Время: {datetime.utcnow().strftime('%H:%M %d.%m')}"
            
            send_telegram_notification.delay(
                chat_id=user.telegram_chat_id,
                message=message
            )
        
    except Exception as e:
        logger.error(f"Failed to send new lead notification: {e}")
    finally:
        session.close()
