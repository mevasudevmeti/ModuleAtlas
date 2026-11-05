from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.llm.factory import create_llm_service


router = APIRouter(
    prefix="/api/v1",
    tags=["chat"],
)

llm_service = create_llm_service()
chat_service = ChatService(llm_service=llm_service)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:

    answer = await chat_service.get_response(request.message)

    return ChatResponse(answer=answer)