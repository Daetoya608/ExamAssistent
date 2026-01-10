from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    is_need_more_context: bool = Field(description="Нужно ли искать информацию в учебных материалах?")
    find_context: str = Field(description="Поисковый запрос для векторной базы данных")
    answer: str = Field(description="Ответ пользователю (если контекст не нужен)")
