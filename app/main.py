import logging
from datetime import date, datetime
from typing import Annotated, Any
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db, init_db
from app.evolution_webhook import parse_evolution_payload
from app.models import WhatsAppMessage
from app.scheduler import create_scheduler
from app.summarizer import summarize_date

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="WhatsApp Obsidian MVP", version="0.1.0")
scheduler = None


@app.on_event("startup")
def on_startup() -> None:
    global scheduler
    settings = get_settings()
    init_db()
    scheduler = create_scheduler(settings)
    scheduler.start()
    logger.info("Application started")


@app.on_event("shutdown")
def on_shutdown() -> None:
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook/evolution", status_code=status.HTTP_202_ACCEPTED)
async def evolution_webhook(
    request: Request,
    x_webhook_token: Annotated[str | None, Header(alias="X-Webhook-Token")] = None,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    if x_webhook_token != settings.webhook_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid webhook token")

    payload = await request.json()
    parsed = parse_evolution_payload(payload)
    if parsed is None:
        logger.warning("Ignoring webhook without message_id")
        return {"status": "ignored", "reason": "missing message_id"}

    statement = (
        insert(WhatsAppMessage)
        .values(
            message_id=parsed.message_id,
            instance=parsed.instance,
            event=parsed.event,
            chat_id=parsed.chat_id,
            chat_name=parsed.chat_name,
            sender_id=parsed.sender_id,
            sender_name=parsed.sender_name,
            from_me=parsed.from_me,
            message_type=parsed.message_type,
            text=parsed.text,
            media_caption=parsed.media_caption,
            media_url=parsed.media_url,
            message_date=parsed.message_date,
            raw_payload=parsed.raw_payload,
        )
        .on_conflict_do_nothing(index_elements=["message_id"])
        .returning(WhatsAppMessage.id)
    )
    inserted_id = db.execute(statement).scalar_one_or_none()
    db.commit()

    if inserted_id is None:
        return {"status": "duplicate", "message_id": parsed.message_id}
    return {"status": "stored", "message_id": parsed.message_id, "id": inserted_id}


@app.post("/summarize/today")
async def summarize_today(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    target_date = datetime.now(ZoneInfo(settings.timezone)).date()
    return await summarize_date(db, settings, target_date)


@app.post("/summarize/{target_date}")
async def summarize_by_date(
    target_date: date,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    return await summarize_date(db, settings, target_date)
