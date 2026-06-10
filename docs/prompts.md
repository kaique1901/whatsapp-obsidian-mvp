# Prompts

O resumo diário usa um prompt único em `app/summarizer.py`.

## Diretrizes

- Gerar Markdown compatível com Obsidian.
- Não inventar informações.
- Usar o modelo configurado em `OLLAMA_MODEL`.
- Manter o frontmatter:

```yaml
---
source: whatsapp
date: YYYY-MM-DD
model: MODEL_NAME
tags:
  - whatsapp
  - resumo-diario
  - ia-local
---
```

## Seções esperadas

- Visão geral
- Principais conversas
- Tarefas identificadas
- Compromissos e datas
- Decisões tomadas
- Pontos de atenção
- Pessoas e grupos relevantes
- Resumo final curto
