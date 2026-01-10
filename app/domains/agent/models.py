from typing import List

from pydantic import BaseModel, Field

from app.domains.chats.schemas import MessageRead


class AgentState(BaseModel):
    """Чистое состояние агента без привязки к LangGraph"""
    answer: str = Field(default=None, description="Ответ от llm")
    history: List[MessageRead] = Field(default_factory=list, description="Последние сообщения")
    is_need_more_context: bool = Field(default=False, description="Нужно ли искать информацию в учебных материалах?")
    find_context: str = Field(default="", description="Поисковый запрос для векторной базы данных")
    extra_context: str = Field(default="Дополнительная информация в базе данных не найдена.", description="доп контекст")
    user_id: int = Field(description="ID пользователя")
    top_k: int = Field(default=10, description="Кол-во доп. контекста")
    context_length: int = Field(default=500, description="Ограничение истории чата")
    find_count: int = Field(default=0, description="Кол-во циклов поиска")
