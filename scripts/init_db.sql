CREATE TABLE IF NOT EXISTS whatsapp_messages (
    id BIGSERIAL PRIMARY KEY,
    message_id VARCHAR(255) NOT NULL UNIQUE,
    instance VARCHAR(255),
    event VARCHAR(255),
    chat_id VARCHAR(255),
    chat_name VARCHAR(255),
    sender_id VARCHAR(255),
    sender_name VARCHAR(255),
    from_me BOOLEAN NOT NULL DEFAULT FALSE,
    message_type VARCHAR(80),
    text TEXT NOT NULL DEFAULT '',
    media_caption TEXT,
    media_url TEXT,
    message_date TIMESTAMPTZ NOT NULL,
    raw_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_whatsapp_messages_message_date ON whatsapp_messages (message_date);
CREATE INDEX IF NOT EXISTS ix_whatsapp_messages_chat_id ON whatsapp_messages (chat_id);
