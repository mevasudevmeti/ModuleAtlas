from app.services.llm.base import LLMService


class ChatService:

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def get_response(self, message: str) -> str:

        system_prompt = (
            "You are ModuleAtlas, an academic knowledge assistant."
        )

        result = await self.llm_service.generate(
            system_prompt=system_prompt,
            user_prompt=message,
        )

        return result.text