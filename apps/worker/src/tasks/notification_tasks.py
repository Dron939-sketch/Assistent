"""
Background tasks for notifications
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta, timezone

from celery import shared_task

from src.database import get_db_session

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@shared_task(name="src.tasks.notification_tasks.send_telegram_notification")
def send_telegram_notification(chat_id: str, message: str):
    """Send notification via Telegram."""
    if not chat_id:
        logger.debug("Skipping telegram notification: empty chat_id")
        return

    logger.info("Sending Telegram notification to %s", chat_id)

    try:
        from src.services.telegram_service import TelegramService
    except ImportError:
        logger.warning("TelegramService is not available; notification skipped")
        return

    try:
        tg_service = TelegramService()
        asyncio.run(tg_service.send_message(chat_id=chat_id, text=message))
        logger.info("Telegram notification sent to %s", chat_id)
    except Exception as e:
        logger.exception("Failed to send Telegram notification: %s", e)


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
        
        now = _utcnow()
        
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
            message += f"Время: {_utcnow().strftime('%H:%M %d.%m')}"
            
            send_telegram_notification.delay(
                chat_id=user.telegram_chat_id,
                message=message
            )
        
    except Exception as e:
        logger.error(f"Failed to send new lead notification: {e}")
    finally:
        session.close()
