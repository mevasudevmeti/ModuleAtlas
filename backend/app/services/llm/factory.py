from app.core.config import get_settings
from app.services.llm.base import LLMService
from app.services.llm.mock import MockLLMService


def create_llm_service() -> LLMService:
    settings = get_settings()

    if settings.llm_provider == "mock":
        return MockLLMService()

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )