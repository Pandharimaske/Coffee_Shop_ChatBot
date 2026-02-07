from langchain_core.runnables import Runnable
from src.utils.util import call_llm
from src.graph.states import CoffeeAgentState
from src.prompts.query_rewrite_prompt import query_rewrite_prompt
from typing import List
from langchain_core.messages import BaseMessage

class QueryRewriterNode(Runnable):
    def __init__(self):
        pass

    def render_messages(self , messages: List[BaseMessage]) -> str:
        return "\n".join(
            f"{msg.type.capitalize()}: {msg.content}" for msg in messages
        )

    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:

        user_input = state["user_input"]
        
        prompt = query_rewrite_prompt.invoke({
            "user_input": state["user_input"] , 
            "messages": self.render_messages(state.get("messages" , [])),
            "chat_summary": state.get("chat_summary", ""),
            "user_memory": str(state.get("user_memory", "")),
            "state": str(state)
        })
        rewritten = call_llm(prompt=prompt)
        state["user_input"] = rewritten.content.strip() if rewritten.content.strip() else user_input
        return state
