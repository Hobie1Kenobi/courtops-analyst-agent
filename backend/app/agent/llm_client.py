from openai import OpenAI

from app.core.config import settings


def get_llm_client() -> OpenAI:
    base_url = settings.ollama_base_url.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1" if "/v1" not in base_url else base_url
    return OpenAI(
        base_url=base_url,
        api_key="ollama",
    )


def get_llm_model() -> str:
    return settings.ollama_model
