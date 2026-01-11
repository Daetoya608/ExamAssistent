from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    is_need_more_context: bool = Field(default=False, description="Нужно ли искать информацию в учебных материалах?")
    find_context: str = Field(default="", description="Поисковый запрос для векторной базы данных")
    answer: str = Field(default="", description="Ответ пользователю (если контекст не нужен)")
