class ChatService:
    async def get_response(self, message: str) -> str:
        return f"ModuleAtlas received: {message}"