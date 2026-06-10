import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

from app.config import Settings
from app.database import SessionLocal
from app.summarizer import summarize_date

logger = logging.getLogger(__name__)


def create_scheduler(settings: Settings) -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone=ZoneInfo(settings.timezone))
    hour, minute = _parse_summary_time(settings.summary_time)
    scheduler.add_job(
        _run_daily_summary,
        CronTrigger(hour=hour, minute=minute, timezone=ZoneInfo(settings.timezone)),
        args=[settings],
        id="daily_whatsapp_summary",
        replace_existing=True,
    )
    return scheduler


def _run_daily_summary(settings: Settings) -> None:
    import asyncio

    target_date = datetime.now(ZoneInfo(settings.timezone)).date()
    db = SessionLocal()
    try:
        asyncio.run(summarize_date(db, settings, target_date))
        logger.info("Daily summary generated for %s", target_date.isoformat())
    except Exception:
        logger.exception("Could not generate daily summary")
    finally:
        db.close()


def _parse_summary_time(value: str) -> tuple[int, int]:
    hour_text, minute_text = value.split(":", maxsplit=1)
    return int(hour_text), int(minute_text)
