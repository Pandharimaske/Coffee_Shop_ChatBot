from langchain_core.runnables import Runnable
from langchain_core.messages import HumanMessage, AIMessage , SystemMessage
from Backend.memory.summary_buffer import ConversationSummaryBufferMessageHistory
from Backend.utils.summary_memory import save_summary
from Backend.graph.states import CoffeeAgentState
from Backend.utils.util import load_llm


class SummaryNode(Runnable):
    def __init__(self, k: int = 6):
        self.history = ConversationSummaryBufferMessageHistory(
            llm=load_llm(),
            k=k
        )

    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        user_id = config["configurable"]["user_id"]
        prev_summary = state.get("chat_summary", "")
        user_input = state["user_input"]
        assistant_response = state["response_message"]

        # Restore previous summary if exists
        if prev_summary:
            self.history.messages.insert(0, SystemMessage(content=prev_summary))

        # Add current turn
        self.history.add_messages([
            HumanMessage(content=user_input),
            AIMessage(content=assistant_response)
        ])

        # Extract updated summary and save
        updated_summary = self.history.get_formatted_memory()
        state["chat_summary"] = updated_summary
        save_summary(user_id, updated_summary)

        return state