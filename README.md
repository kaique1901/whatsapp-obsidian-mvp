# WhatsApp Obsidian MVP

MVP local para receber mensagens do WhatsApp via Evolution API, salvar no PostgreSQL, gerar resumos com Ollama e gravar notas Markdown em um vault do Obsidian.

## Stack

- Python 3.12
- FastAPI
- PostgreSQL
- Ollama local
- Docker Compose / Portainer
- Obsidian via volume Docker

## Configuração

1. Copie `.env.example` para `.env`.
2. Troque `WEBHOOK_TOKEN` e `POSTGRES_PASSWORD`.
3. Ajuste `OBSIDIAN_VAULT_PATH` para o caminho absoluto do seu vault.
4. Suba a stack:

```bash
docker compose up -d --build
```

5. Baixe um modelo leve no Ollama:

```bash
docker exec -it whatsapp_obsidian_ollama ollama pull qwen2.5:3b
```

## Portainer

No Portainer, crie uma nova stack usando o conteúdo de `docker-compose.yml`.
Cadastre as variáveis do `.env` na stack ou envie o arquivo `.env` junto do projeto.

## Webhook da Evolution API

Configure a Evolution API para enviar eventos para:

```text
POST http://SEU_HOST:8000/webhook/evolution
Header: X-Webhook-Token: seu-token
```

O endpoint aceita textos, mensagens estendidas e legendas de imagem, vídeo ou documento.
Mensagens duplicadas são ignoradas por `message_id`.

## Resumos

Gerar resumo de hoje:

```bash
curl -X POST http://localhost:8000/summarize/today
```

Gerar resumo de uma data:

```bash
curl -X POST http://localhost:8000/summarize/2026-06-10
```

O arquivo final será salvo em:

```text
/obsidian/WhatsApp/Daily/YYYY-MM-DD.md
```

Dentro do host, esse caminho corresponde a:

```text
${OBSIDIAN_VAULT_PATH}/WhatsApp/Daily/YYYY-MM-DD.md
```

## Agendamento

O resumo diário roda automaticamente no horário definido por `SUMMARY_TIME`.
O fuso horário padrão é `America/Sao_Paulo`.

## Segurança

- Não use o valor padrão de `WEBHOOK_TOKEN`.
- Não exponha Ollama, PostgreSQL ou a API diretamente na internet sem proxy/autenticação.
- Não versione `.env`, banco de dados ou arquivos reais do vault.
