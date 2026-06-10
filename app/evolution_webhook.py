from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class ParsedMessage:
    message_id: str
    instance: str | None
    event: str | None
    chat_id: str | None
    chat_name: str | None
    sender_id: str | None
    sender_name: str | None
    from_me: bool
    message_type: str | None
    text: str
    media_caption: str | None
    media_url: str | None
    message_date: datetime
    raw_payload: dict[str, Any]


def parse_evolution_payload(payload: dict[str, Any]) -> ParsedMessage | None:
    data = _as_dict(payload.get("data")) or payload
    key = _as_dict(data.get("key"))
    message = _as_dict(data.get("message"))

    message_id = _first_text(
        key.get("id"),
        data.get("id"),
        data.get("messageId"),
        payload.get("messageId"),
    )
    if not message_id:
        return None

    message_type = _detect_message_type(message, data)
    text, caption, media_url = _extract_text_caption_and_media(message, data, message_type)

    chat_id = _first_text(
        key.get("remoteJid"),
        data.get("remoteJid"),
        data.get("chatId"),
        data.get("jid"),
    )
    sender_id = _first_text(
        key.get("participant"),
        data.get("participant"),
        data.get("sender"),
        data.get("senderId"),
        chat_id,
    )
    push_name = _first_text(data.get("pushName"), data.get("senderName"), data.get("name"))

    return ParsedMessage(
        message_id=message_id,
        instance=_first_text(payload.get("instance"), data.get("instance")),
        event=_first_text(payload.get("event"), data.get("event")),
        chat_id=chat_id,
        chat_name=_first_text(data.get("chatName"), data.get("groupName")),
        sender_id=sender_id,
        sender_name=push_name,
        from_me=bool(key.get("fromMe") or data.get("fromMe") or False),
        message_type=message_type,
        text=text or caption or "",
        media_caption=caption,
        media_url=media_url,
        message_date=_parse_message_datetime(data),
        raw_payload=payload,
    )


def _detect_message_type(message: dict[str, Any], data: dict[str, Any]) -> str | None:
    explicit_type = _first_text(data.get("messageType"), data.get("type"))
    if explicit_type:
        return explicit_type
    for key in (
        "conversation",
        "extendedTextMessage",
        "imageMessage",
        "videoMessage",
        "documentMessage",
        "audioMessage",
        "stickerMessage",
    ):
        if key in message:
            return key
    return None


def _extract_text_caption_and_media(
    message: dict[str, Any],
    data: dict[str, Any],
    message_type: str | None,
) -> tuple[str, str | None, str | None]:
    text = _first_text(
        data.get("text"),
        data.get("body"),
        message.get("conversation"),
        _as_dict(message.get("extendedTextMessage")).get("text"),
    )

    typed_message = _as_dict(message.get(message_type or ""))
    caption = _first_text(
        data.get("caption"),
        typed_message.get("caption"),
        _as_dict(message.get("imageMessage")).get("caption"),
        _as_dict(message.get("videoMessage")).get("caption"),
        _as_dict(message.get("documentMessage")).get("caption"),
    )
    media_url = _first_text(
        data.get("mediaUrl"),
        data.get("url"),
        typed_message.get("url"),
        _as_dict(message.get("imageMessage")).get("url"),
        _as_dict(message.get("videoMessage")).get("url"),
        _as_dict(message.get("documentMessage")).get("url"),
    )
    return text or "", caption, media_url


def _parse_message_datetime(data: dict[str, Any]) -> datetime:
    raw = data.get("messageTimestamp") or data.get("timestamp") or data.get("dateTime")
    if isinstance(raw, (int, float)):
        timestamp = raw / 1000 if raw > 10_000_000_000 else raw
        return datetime.fromtimestamp(timestamp, tz=UTC)
    if isinstance(raw, str):
        try:
            normalized = raw.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(normalized)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            pass
    return datetime.now(tz=UTC)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _first_text(*values: Any) -> str | None:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None
