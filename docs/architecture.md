# Arquitetura

Este MVP roda como uma stack Docker local pensada para Portainer.

## Componentes

- `api`: aplicação FastAPI que recebe webhooks da Evolution API, persiste mensagens e gera resumos.
- `postgres`: banco local usado para armazenar mensagens e payload bruto em `JSONB`.
- `ollama`: runtime local de IA. Nenhuma API externa de IA é usada.
- `obsidian`: volume montado no container da API em `/obsidian`.

## Fluxo

1. A Evolution API envia eventos para `POST /webhook/evolution`.
2. A API valida o header `X-Webhook-Token`.
3. O payload é interpretado por `app/evolution_webhook.py`.
4. A mensagem é inserida no PostgreSQL com `message_id` único.
5. `POST /summarize/today` ou `POST /summarize/{date}` carrega mensagens do dia.
6. A API chama o Ollama em `/api/generate`.
7. O Markdown final é salvo em `/obsidian/WhatsApp/Daily/YYYY-MM-DD.md`.

## Observações

O parser é tolerante a variações comuns da Evolution API e preserva sempre o payload bruto.
Se a API de webhook mudar, ajuste somente `app/evolution_webhook.py`.
