from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import WhatsAppMessage
from app.obsidian_writer import write_daily_note
from app.ollama_client import OllamaClient


async def summarize_date(db: Session, settings: Settings, target_date: date) -> dict[str, str]:
    messages = _load_messages_for_date(db, settings, target_date)
    prompt = _build_prompt(settings, target_date, messages)
    summary = await OllamaClient(settings).generate(prompt)
    markdown = _ensure_markdown_note(settings, target_date, summary)
    path = write_daily_note(settings, target_date, markdown)
    return {
        "date": target_date.isoformat(),
        "messages": str(len(messages)),
        "path": str(path),
        "model": settings.ollama_model,
    }


def _load_messages_for_date(db: Session, settings: Settings, target_date: date) -> list[WhatsAppMessage]:
    tz = ZoneInfo(settings.timezone)
    start = datetime.combine(target_date, time.min, tzinfo=tz)
    end = datetime.combine(target_date, time.max, tzinfo=tz)
    statement = (
        select(WhatsAppMessage)
        .where(WhatsAppMessage.message_date >= start)
        .where(WhatsAppMessage.message_date <= end)
        .order_by(WhatsAppMessage.message_date.asc(), WhatsAppMessage.id.asc())
    )
    return list(db.scalars(statement).all())


def _build_prompt(settings: Settings, target_date: date, messages: list[WhatsAppMessage]) -> str:
    transcript = "\n".join(_format_message(message) for message in messages)
    if not transcript:
        transcript = "Nenhuma mensagem encontrada para esta data."

    return f"""
Você é um assistente local rodando via Ollama. Gere uma nota Markdown compatível com Obsidian.
Não invente informações. Quando não houver dados para uma seção, escreva "Nada identificado".

Use exatamente esta estrutura:

---
source: whatsapp
date: {target_date.isoformat()}
model: {settings.ollama_model}
tags:
  - whatsapp
  - resumo-diario
  - ia-local
---

# Resumo WhatsApp - {target_date.isoformat()}

## Visão geral

## Principais conversas

## Tarefas identificadas
- [ ]

## Compromissos e datas

## Decisões tomadas

## Pontos de atenção

## Pessoas e grupos relevantes

## Resumo final curto

Mensagens do dia:
{transcript}
""".strip()


def _format_message(message: WhatsAppMessage) -> str:
    timestamp = message.message_date.isoformat()
    direction = "enviada" if message.from_me else "recebida"
    chat = message.chat_name or message.chat_id or "chat desconhecido"
    sender = message.sender_name or message.sender_id or "remetente desconhecido"
    text = message.text.strip() or "[sem texto]"
    return f"- [{timestamp}] ({direction}) {chat} | {sender}: {text}"


def _ensure_markdown_note(settings: Settings, target_date: date, summary: str) -> str:
    if summary.lstrip().startswith("---") and f"date: {target_date.isoformat()}" in summary:
        return summary.rstrip() + "\n"
    return f"""---
source: whatsapp
date: {target_date.isoformat()}
model: {settings.ollama_model}
tags:
  - whatsapp
  - resumo-diario
  - ia-local
---

# Resumo WhatsApp - {target_date.isoformat()}

{summary.strip()}
"""
