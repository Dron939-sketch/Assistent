"""
Background tasks for VK audit
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from celery import shared_task

from src.services.vk_service import VKService
from src.services.audit_service import AuditService
from src.database import get_db_session

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@shared_task(name="src.tasks.audit_tasks.run_vk_audit", bind=True, max_retries=3)
def run_vk_audit(self, audit_id: str, group_id: str, user_id: str):
    """Run VK page audit in background."""
    logger.info("Starting VK audit group=%s audit=%s", group_id, audit_id)

    from src.models.audit import VKAudit, VKAuditDetail

    session = get_db_session()
    audit = None

    try:
        audit = session.query(VKAudit).filter(VKAudit.id == uuid.UUID(audit_id)).first()
        if not audit:
            logger.error("Audit %s not found", audit_id)
            return

        audit.status = "processing"
        session.commit()

        audit_service = AuditService()
        result = asyncio.run(audit_service.audit_vk_page(group_id, user_id))

        categories = result.get("categories", [])
        total_score = sum(cat.get("score", 0) for cat in categories)
        max_score = sum(cat.get("max_score", 10) for cat in categories)
        final_score = int((total_score / max_score) * 100) if max_score > 0 else 0

        audit.status = "completed"
        audit.score = final_score
        audit.result = result
        audit.recommendations = result.get("global_recommendations", {})
        audit.completed_at = _utcnow()
        session.commit()

        for cat in categories:
            session.add(
                VKAuditDetail(
                    audit_id=audit.id,
                    category=cat.get("category"),
                    score=cat.get("score", 0),
                    max_score=cat.get("max_score", 10),
                    issues=cat.get("issues", []),
                    recommendations=cat.get("recommendations", []),
                )
            )
        session.commit()
        logger.info("VK audit %s completed with score %s", audit_id, final_score)

    except Exception as e:
        logger.exception("VK audit %s failed: %s", audit_id, e)
        if audit is not None:
            audit.status = "failed"
            audit.error_message = str(e)
            session.commit()
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

    finally:
        session.close()


@shared_task(name="src.tasks.audit_tasks.refresh_vk_data")
def refresh_vk_data(user_id: str, vk_group_id: str):
    """Refresh cached VK data for user."""
    logger.info("Refreshing VK data user=%s group=%s", user_id, vk_group_id)

    vk_service = VKService()

    async def _fetch():
        info = await vk_service.get_group_info(vk_group_id)
        posts = await vk_service.get_wall_posts(vk_group_id, count=20)
        return info, posts

    group_info, posts = asyncio.run(_fetch())

    from celery import current_app
    current_app.backend.set(
        f"vk_data:{user_id}",
        {
            "group_info": group_info,
            "posts": posts,
            "updated_at": _utcnow().isoformat(),
        },
    )

    logger.info("VK data refreshed user=%s", user_id)
