"""
Celery application configuration
"""

from celery import Celery
from celery.schedules import crontab
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis URL from environment
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/fishflow")

# Create Celery app
celery_app = Celery(
    "fishflow_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "src.tasks.audit_tasks",
        "src.tasks.content_tasks",
        "src.tasks.marathon_tasks",
        "src.tasks.funnel_tasks",
        "src.tasks.notification_tasks",
        "src.tasks.analytics_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    
    # Task execution
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    
    # Task retries
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Result retention
    result_expires=3600,  # 1 hour
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    
    # Rate limits
    task_annotations={
        "src.tasks.funnel_tasks.process_webhook_message": {"rate_limit": "10/s"},
        "src.tasks.funnel_tasks.send_auto_reply": {"rate_limit": "30/m"}
    }
)

# Scheduled tasks (beat schedule)
celery_app.conf.beat_schedule = {
    # Daily analytics aggregation (every day at 23:55)
    "aggregate-daily-analytics": {
        "task": "src.tasks.analytics_tasks.aggregate_daily_analytics",
        "schedule": crontab(hour=23, minute=55),
        "options": {"expires": 60 * 60}
    },
    
    # Generate leverage points (every Monday at 09:00)
    "generate-leverage-points": {
        "task": "src.tasks.analytics_tasks.generate_leverage_points_task",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),
        "options": {"expires": 60 * 60}
    },
    
    # Check expired subscriptions (every day at 00:00)
    "check-expired-subscriptions": {
        "task": "src.tasks.notification_tasks.check_expired_subscriptions",
        "schedule": crontab(hour=0, minute=0),
        "options": {"expires": 15 * 60}
    },
    
    # Send scheduled posts (every 15 minutes)
    "send-scheduled-posts": {
        "task": "src.tasks.content_tasks.send_scheduled_posts",
        "schedule": crontab(minute="*/15"),
        "options": {"expires": 5 * 60}
    },
    
    # Refresh VK analytics for active users (every day at 08:00)
    "refresh-vk-analytics": {
        "task": "src.tasks.analytics_tasks.refresh_vk_analytics",
        "schedule": crontab(hour=8, minute=0),
        "options": {"expires": 60 * 60}
    },
    
    # Marathon daily sends (every 5 minutes)
    "process-marathon-daily-sends": {
        "task": "src.tasks.marathon_tasks.process_daily_marathon_sends",
        "schedule": crontab(minute="*/5"),
        "options": {"expires": 2 * 60}
    },
    
    # Cleanup stale sessions (every hour)
    "cleanup-stale-sessions": {
        "task": "src.tasks.funnel_tasks.cleanup_stale_sessions",
        "schedule": crontab(minute=0),
        "options": {"expires": 30 * 60}
    }
}

if __name__ == "__main__":
    celery_app.start()
