from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from Backend.utils.util import load_llm
from Backend.graph.states import CoffeeAgentState
from Backend.prompts.query_rewrite_prompt import query_rewrite_prompt
from typing import List
from langchain_core.messages import BaseMessage
from Backend.utils.memory_manager import get_user_memory
from Backend.utils.summary_memory import get_summary , get_messages


class QueryRewriterNode(Runnable):
    def __init__(self):
        self.llm = load_llm()
        self.prompt = query_rewrite_prompt
        self.chain = self.prompt | self.llm | StrOutputParser()

    def render_messages(self , messages: List[BaseMessage]) -> str:
        return "\n".join(
            f"{msg.type.capitalize()}: {msg.content}" for msg in messages
        )

    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        user_id = config["configurable"]["user_id"]
        state["user_memory"] = get_user_memory(user_id)
        state["chat_summary"] = get_summary(id=user_id)
        state["messages"] = get_messages(id = user_id)

        rewritten = self.chain.invoke({
            "user_input": state["user_input"] , 
            "messages": self.render_messages(state.get("messages" , [])),
            "chat_summary": state.get("chat_summary", ""),
            "user_memory": str(state.get("user_memory", "")),
            "state": str(state)
        })
        state["user_input"] = rewritten.strip()
        return state
