from langchain_core.runnables import Runnable
from langchain_core.messages import BaseMessage, SystemMessage
from Backend.memory.summary_buffer import ConversationSummaryMemory
from Backend.utils.summary_memory import save_summary , save_messages
from Backend.graph.states import CoffeeAgentState
from Backend.utils.util import load_llm


class SummaryNode(Runnable):
    def __init__(self, k: int = 6):
        self.k = k
        self.llm = load_llm()

    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        user_id = config["configurable"]["user_id"]
        all_messages: list[BaseMessage] = state.get("messages", [])
        prev_summary = state.get("chat_summary", "")

        # If messages are fewer than or equal to k, skip summarization
        if len(all_messages) <= self.k:
            return CoffeeAgentState(**state)

        # Split messages into old (to summarize) and recent (to keep)
        old_messages = all_messages[-2:]
        recent_messages = all_messages[:-2] 

        # Create summarizer and insert previous summary
        history = ConversationSummaryMemory()

        if prev_summary:
            history.add_messages([SystemMessage(content=prev_summary)])

        # Add old messages to summarizer
        history.add_messages(old_messages)

        # Generate new summary
        updated_summary = history.get_formatted_memory()

        # Save Memory and Messages
        state["chat_summary"] = updated_summary
        state["messages"] = recent_messages
        save_summary(user_id, updated_summary)
        save_messages(user_id , recent_messages)

        return CoffeeAgentState(**state)