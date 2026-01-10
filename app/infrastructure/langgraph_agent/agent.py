from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END

from app.domains.agent.interface import AgentInterface
from app.domains.agent.models import AgentState
from app.domains.chats.service import ChatService
from app.domains.llm.interface import LLMInterface
from app.domains.vector_db.service import VectorDBService
from app.infrastructure.langgraph_agent.nodes import (get_messages_node, ask_llm_node, get_extra_context_node,
                                                      check_context_need)


class LangGraphAIAgent(AgentInterface):
    def __init__(self):
        self.graph = self._build_graph()


    def _build_graph(self):
        builder = StateGraph(AgentState)

        builder.add_node("get_messages_node", get_messages_node)
        builder.add_node("ask_llm_node", ask_llm_node)
        builder.add_node("get_extra_context_node", get_extra_context_node)

        builder.add_edge(START, "get_messages_node")
        builder.add_edge("get_messages_node", "ask_llm_node")
        builder.add_edge("get_extra_context_node", "ask_llm_node")

        builder.add_conditional_edges(
            "ask_llm_node",
            check_context_need,
            {
                "need_context": "get_extra_context_node",
                "just_answer": END
            }
        )

        app = builder.compile()
        return app


    def process_sync(
            self,
            user_id: int,
            chat_service: ChatService,
            llm: LLMInterface,
            vector_db_service: VectorDBService,
    ) -> str:
        config = {
            "configurable": {
                "chat_service": chat_service,
                "llm": llm,
                "vector_db_service": vector_db_service,
            }
        }


        response = self.graph.invoke(
            AgentState(user_id=user_id).model_dump(),
            config=config,
        )
        return response["answer"]


graph = LangGraphAIAgent()
