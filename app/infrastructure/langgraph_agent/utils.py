from typing import List

from app.domains.chats.schemas import MessageRead, AuthorRole
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.prompt_values import PromptValue
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser

from app.infrastructure.langgraph_agent.prompts import MAIN_SYSTEM_PROMPT_TEXT
from app.infrastructure.langgraph_agent.schemas import LLMResponse


def analyze_messages_prompt(messages: List[BaseMessage],
                            extra_context: str = "Дополнительная информация в базе данных не найдена.",
                            parser: JsonOutputParser = JsonOutputParser(pydantic_object=LLMResponse)) -> PromptValue:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=MAIN_SYSTEM_PROMPT_TEXT),
        MessagesPlaceholder(variable_name="chat_history"),
        SystemMessage(content="Вспомни: твой ответ должен быть СТРОГО в формате JSON по указанной схеме."
                              "Не пиши ничего, кроме JSON."),
    ])
    final_prompt = prompt.partial(
        format_instructions=parser.get_format_instructions(),
        extra_context=extra_context,
    )
    return final_prompt.invoke({"chat_history": messages})


def convert_to_langchain_messages(messages: List[MessageRead]) -> List[BaseMessage]:
    result_messages = []
    for message in messages:
        if message.author == AuthorRole.HUMAN:
            result_messages.append(message.text)
        elif message.author == AuthorRole.AI:
            result_messages.append(message.text)
        elif message.author == AuthorRole.SYSTEM:
            result_messages.append(message.text)
    return result_messages


