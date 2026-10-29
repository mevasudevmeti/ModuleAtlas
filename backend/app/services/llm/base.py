from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResult:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int


class LLMService(ABC):

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> LLMResult:
        pass