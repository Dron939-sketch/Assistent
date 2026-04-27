"""
Background tasks for VK audit
"""

from celery import shared_task
import logging
from datetime import datetime
import uuid

from src.services.vk_service import VKService
from src.services.audit_service import AuditService
from src.database import get_db_session

logger = logging.getLogger(__name__)


@shared_task(name="src.tasks.audit_tasks.run_vk_audit", bind=True, max_retries=3)
def run_vk_audit(self, audit_id: str, group_id: str, user_id: str):
    """
    Run VK page audit in background
    """
    logger.info(f"Starting VK audit for group {group_id}, audit_id={audit_id}")
    
    from src.models.audit import VKAudit, VKAuditDetail
    
    session = get_db_session()
    
    try:
        # Update status to processing
        audit = session.query(VKAudit).filter(VKAudit.id == uuid.UUID(audit_id)).first()
        if not audit:
            logger.error(f"Audit {audit_id} not found")
            return
        
        audit.status = "processing"
        session.commit()
        
        # Run audit
        audit_service = AuditService()
        
        # This is a sync wrapper around async method
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            audit_service.audit_vk_page(group_id, user_id)
        )
        loop.close()
        
        # Calculate scores
        categories = result.get("categories", [])
        total_score = sum(cat.get("score", 0) for cat in categories)
        max_score = sum(cat.get("max_score", 10) for cat in categories)
        final_score = int((total_score / max_score) * 100) if max_score > 0 else 0
        
        # Update audit record
        audit.status = "completed"
        audit.score = final_score
        audit.result = result
        audit.recommendations = result.get("global_recommendations", {})
        audit.completed_at = datetime.utcnow()
        session.commit()
        
        # Insert category details
        for cat in categories:
            detail = VKAuditDetail(
                audit_id=audit.id,
                category=cat.get("category"),
                score=cat.get("score", 0),
                max_score=cat.get("max_score", 10),
                issues=cat.get("issues", []),
                recommendations=cat.get("recommendations", [])
            )
            session.add(detail)
        
        session.commit()
        logger.info(f"VK audit {audit_id} completed with score {final_score}")
        
    except Exception as e:
        logger.error(f"VK audit {audit_id} failed: {e}")
        
        # Update status to failed
        if 'audit' in locals():
            audit.status = "failed"
            audit.error_message = str(e)
            session.commit()
        
        # Retry
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    
    finally:
        session.close()


@shared_task(name="src.tasks.audit_tasks.refresh_vk_data")
def refresh_vk_data(user_id: str, vk_group_id: str):
    """
    Refresh cached VK data for user
    """
    logger.info(f"Refreshing VK data for user {user_id}, group {vk_group_id}")
    
    vk_service = VKService()
    
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    group_info = loop.run_until_complete(vk_service.get_group_info(vk_group_id))
    posts = loop.run_until_complete(vk_service.get_wall_posts(vk_group_id, count=20))
    
    loop.close()
    
    # Store in cache (Redis would be better)
    from celery import current_app
    cache_key = f"vk_data:{user_id}"
    current_app.backend.set(cache_key, {
        "group_info": group_info,
        "posts": posts,
        "updated_at": datetime.utcnow().isoformat()
    })
    
    logger.info(f"VK data refreshed for user {user_id}")
