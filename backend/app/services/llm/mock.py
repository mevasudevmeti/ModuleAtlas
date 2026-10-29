from app.services.llm.base import LLMResult, LLMService


class MockLLMService(LLMService):

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> LLMResult:

        return LLMResult(
            text=f"Mock response to: {user_prompt}",
            model="mock-v1",
            input_tokens=0,
            output_tokens=0,
            latency_ms=0,
        )