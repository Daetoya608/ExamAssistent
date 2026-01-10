from langgraph.config import RunnableConfig
from langchain_core.output_parsers import JsonOutputParser

from app.domains.documents.utils import format_chunks_to_context
from app.domains.agent.models import AgentState
from app.domains.chats.schemas import MessageInput, AuthorRole
from app.domains.chats.service import ChatService
from app.domains.llm.interface import LLMInterface
from app.domains.vector_db.service import VectorDBService
from app.infrastructure.langgraph_agent.schemas import LLMResponse
from app.infrastructure.langgraph_agent.utils import analyze_messages_prompt, convert_to_langchain_messages


def get_messages_node(state: AgentState, config: RunnableConfig):
    # Получаем зависимости
    chat_service: ChatService = config["configurable"]["chat_service"]
    context_length = state.context_length

    # Получаем последние сообщения
    context_messages = chat_service.get_last_messages_sync(context_length)

    state.history = context_messages
    return state


def ask_llm_node(state: AgentState, config: RunnableConfig):
    # Получение зависимостей
    llm: LLMInterface = config["configurable"]["llm"]
    parser = JsonOutputParser(pydantic_object=LLMResponse)

    # Составление промпта
    messages = convert_to_langchain_messages(state.history)
    prompt = analyze_messages_prompt(messages=messages, extra_context=state.extra_context, parser=parser)

    # Получение ответа от ллм
    answer = llm.invoke(prompt)

    # Парсинг ответа
    parsed_answer = parser.invoke(answer)
    result = LLMResponse(**parsed_answer)

    # Обновление состояний
    state.answer = result.answer
    state.is_need_more_context = result.is_need_more_context
    state.find_context = result.find_context

    return state


def get_extra_context_node(state: AgentState, config: RunnableConfig):
    # Получение зависимостей
    vector_db_service: VectorDBService = config["configurable"]["vector_db_service"]

    # Поиск по контексту
    chunks = vector_db_service.vector_storage.search(
        query_text=state.find_context,
        user_id=state.user_id,
        top_k=state.top_k,
    )
    extra_context = format_chunks_to_context(chunks)
    state.extra_context = extra_context
    state.find_count += 1

    return state


def check_context_need(state: AgentState):
    if state.is_need_more_context and state.find_count < 3:
        return "need_context"
    else:
        return "just_answer"



