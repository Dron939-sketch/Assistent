"""
Background tasks for auto funnel
"""

from celery import shared_task
import logging
from datetime import datetime, timedelta
import uuid

from src.services.vk_service import VKService
from src.services.ai_service import AIService
from src.database import get_db_session

logger = logging.getLogger(__name__)


@shared_task(name="src.tasks.funnel_tasks.process_webhook_message", bind=True, max_retries=2)
def process_webhook_message(self, message_data: dict, funnel_id: str, lead_id: str):
    """
    Process incoming VK message through funnel
    """
    logger.info(f"Processing webhook message for funnel {funnel_id}, lead {lead_id}")
    
    session = get_db_session()
    
    try:
        from src.models.funnel import AutoFunnel, Lead, FunnelSession
        
        funnel = session.query(AutoFunnel).filter(AutoFunnel.id == uuid.UUID(funnel_id)).first()
        lead = session.query(Lead).filter(Lead.id == uuid.UUID(lead_id)).first()
        
        if not funnel or not lead:
            logger.error(f"Funnel or lead not found")
            return
        
        # Get or create session
        funnel_session = session.query(FunnelSession).filter(
            FunnelSession.lead_id == lead.id,
            FunnelSession.is_active == True
        ).first()
        
        if not funnel_session:
            funnel_session = FunnelSession(
                funnel_id=funnel.id,
                lead_id=lead.id,
                current_step=1
            )
            session.add(funnel_session)
            session.commit()
        
        # Get current step
        steps = funnel.flow_steps
        current_step_num = funnel_session.current_step
        
        # Find step
        current_step = None
        for step in steps:
            if step.get("step") == current_step_num:
                current_step = step
                break
        
        if not current_step:
            # Use fallback
            response_text = funnel.fallback_message or "Спасибо за сообщение! Эксперт свяжется с вами."
        else:
            step_type = current_step.get("type")
            step_content = current_step.get("content")
            
            # Replace placeholders
            step_content = step_content.replace("[name]", lead.name or "гость")
            
            if step_type == "ask_contact":
                response_text = step_content
                # Expect user to provide contact
                funnel_session.context["awaiting_contact"] = True
            elif step_type == "send_material":
                response_text = step_content
                # Track that material was sent
                funnel_session.context["material_sent"] = True
            elif step_type == "ask_booking":
                response_text = step_content
                funnel_session.context["awaiting_booking"] = True
            else:
                response_text = step_content
        
        # Send response
        vk_service = VKService()
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            vk_service.send_message(
                peer_id=int(lead.vk_user_id),
                message=response_text
            )
        )
        loop.close()
        
        # Update conversation
        conversation = lead.conversation or []
        conversation.append({
            "role": "assistant",
            "content": response_text,
            "step": current_step_num,
            "timestamp": datetime.utcnow().isoformat()
        })
        lead.conversation = conversation
        
        # Move to next step
        funnel_session.current_step = current_step_num + 1
        funnel_session.last_message_at = datetime.utcnow()
        session.commit()
        
        # Schedule next step if delay exists
        delay_minutes = current_step.get("delay_minutes", 0)
        if delay_minutes > 0 and funnel_session.current_step <= len(steps):
            # Schedule reminder
            schedule_followup.apply_async(
                args=[str(funnel_session.id)],
                countdown=delay_minutes * 60
            )
        
        logger.info(f"Processed message, moved to step {funnel_session.current_step}")
        
    except Exception as e:
        logger.error(f"Failed to process webhook message: {e}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    finally:
        session.close()


@shared_task(name="src.tasks.funnel_tasks.schedule_followup")
def schedule_followup(funnel_session_id: str):
    """
    Send follow-up message after delay
    """
    logger.info(f"Sending follow-up for session {funnel_session_id}")
    
    session = get_db_session()
    
    try:
        from src.models.funnel import FunnelSession, AutoFunnel, Lead
        
        funnel_session = session.query(FunnelSession).filter(
            FunnelSession.id == uuid.UUID(funnel_session_id),
            FunnelSession.is_active == True
        ).first()
        
        if not funnel_session:
            logger.warning(f"Session {funnel_session_id} not found or inactive")
            return
        
        funnel = session.query(AutoFunnel).filter(
            AutoFunnel.id == funnel_session.funnel_id
        ).first()
        
        lead = session.query(Lead).filter(
            Lead.id == funnel_session.lead_id
        ).first()
        
        if not funnel or not lead:
            return
        
        steps = funnel.flow_steps
        current_step_num = funnel_session.current_step - 1  # Get the step we're following up on
        
        # Find the step that had delay
        step = None
        for s in steps:
            if s.get("step") == current_step_num:
                step = s
                break
        
        if step and step.get("followup_message"):
            response_text = step.get("followup_message")
            response_text = response_text.replace("[name]", lead.name or "гость")
            
            # Send
            vk_service = VKService()
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                vk_service.send_message(
                    peer_id=int(lead.vk_user_id),
                    message=response_text
                )
            )
            loop.close()
        
        logger.info(f"Follow-up sent for session {funnel_session_id}")
        
    except Exception as e:
        logger.error(f"Failed to send follow-up: {e}")
    finally:
        session.close()


@shared_task(name="src.tasks.funnel_tasks.cleanup_stale_sessions")
def cleanup_stale_sessions():
    """
    Clean up stale funnel sessions (older than 7 days)
    """
    logger.info("Cleaning up stale funnel sessions")
    
    session = get_db_session()
    
    try:
        from src.models.funnel import FunnelSession
        
        cutoff = datetime.utcnow() - timedelta(days=7)
        
        stale = session.query(FunnelSession).filter(
            FunnelSession.last_message_at < cutoff,
            FunnelSession.is_active == True
        ).all()
        
        for s in stale:
            s.is_active = False
        
        session.commit()
        logger.info(f"Cleaned up {len(stale)} stale sessions")
        
    except Exception as e:
        logger.error(f"Failed to cleanup stale sessions: {e}")
    finally:
        session.close()
