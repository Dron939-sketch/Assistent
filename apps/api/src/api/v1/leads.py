"""
Early-access lead intake.

Frontend posts here from the landing modal. We log it loudly (so the
Render dashboard always shows the trail) and forward to a Telegram chat
if `TELEGRAM_LEAD_CHAT_ID` is configured. No DB dependency — this works
even before Postgres is wired up.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

router = APIRouter()
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get(
    "TELEGRAM_TOKEN"
)
TELEGRAM_LEAD_CHAT_ID = os.environ.get("TELEGRAM_LEAD_CHAT_ID")


class EarlyAccessLead(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    contact: str = Field(..., min_length=1, max_length=200)
    niche: Optional[str] = Field(default=None, max_length=2000)
    source: Optional[str] = Field(default=None, max_length=100)


class EarlyAccessResponse(BaseModel):
    ok: bool
    queued_telegram: bool


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _notify_telegram(payload: EarlyAccessLead) -> bool:
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_LEAD_CHAT_ID):
        return False

    text = (
        "🟢 *Новая заявка FishFlow*\n"
        f"*Имя:* {payload.name}\n"
        f"*Контакт:* {payload.contact}\n"
        f"*Ниша:* {payload.niche or '—'}\n"
        f"*Источник:* {payload.source or 'landing'}\n"
        f"*Время:* {datetime.now(timezone.utc).isoformat(timespec='seconds')}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                url,
                json={
                    "chat_id": TELEGRAM_LEAD_CHAT_ID,
                    "text": text,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True,
                },
            )
        if r.status_code >= 400:
            logger.warning(
                "leads.telegram non-2xx status=%s body=%s",
                r.status_code,
                r.text[:500],
            )
            return False
        return True
    except Exception:
        logger.exception("leads.telegram failed")
        return False


@router.post("/early-access", response_model=EarlyAccessResponse)
async def submit_early_access(payload: EarlyAccessLead, request: Request):
    if not payload.name.strip() or not payload.contact.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="name and contact are required",
        )

    logger.info(
        "leads.early_access name=%s contact=%s niche=%s source=%s ip=%s",
        payload.name,
        payload.contact,
        (payload.niche or "")[:80],
        payload.source,
        _client_ip(request),
    )

    queued = await _notify_telegram(payload)
    return EarlyAccessResponse(ok=True, queued_telegram=queued)
