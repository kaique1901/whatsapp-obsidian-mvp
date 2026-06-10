from datetime import date
from pathlib import Path

from app.config import Settings


def write_daily_note(settings: Settings, target_date: date, markdown: str) -> Path:
    daily_dir = Path(settings.obsidian_daily_dir)
    daily_dir.mkdir(parents=True, exist_ok=True)
    output_path = daily_dir / f"{target_date.isoformat()}.md"
    output_path.write_text(markdown, encoding="utf-8")
    return output_path
