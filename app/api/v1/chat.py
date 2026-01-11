from loguru import logger

import io

from fastapi import APIRouter, UploadFile, File, Depends

from app.api.dependencies import get_chat_use_case
from app.domains.users.schemas import UserRead
from app.application.use_cases.chat import ChatUseCase
from app.domains.chats.schemas import MessageUserInput

router = APIRouter()


@router.post("/chat")
async def chat(
        message: MessageUserInput,
        use_case: ChatUseCase = Depends(get_chat_use_case)
):
    logger.info(f"chat: {message}")

    result = use_case.execute(new_message=message.text)

    if result:
        return {"status": "success", "answer": result}
    else:
        return {"status": "error"}
