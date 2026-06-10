import httpx

from app.config import Settings


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate(self, prompt: str) -> str:
        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 8192,
            },
        }
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(url, json=payload)
        if response.status_code >= 400:
            raise OllamaError(f"Ollama returned HTTP {response.status_code}")
        data = response.json()
        text = data.get("response")
        if not isinstance(text, str) or not text.strip():
            raise OllamaError("Ollama returned an empty response")
        return text.strip()
