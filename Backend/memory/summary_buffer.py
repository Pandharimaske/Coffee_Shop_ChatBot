from typing import List
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from Backend.utils.util import load_llm
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate


class ConversationSummaryBufferMessageHistory(BaseModel):
    messages: List[BaseMessage] = Field(default_factory=list)
    llm: ChatGroq = Field(default_factory=lambda: load_llm())
    k: int = Field(default=6)  # Number of messages to keep in buffer

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add messages and summarize older ones if beyond limit."""
        existing_summary = None
        old_messages = None

        # If the first message is a summary
        if self.messages and isinstance(self.messages[0], SystemMessage):
            existing_summary = self.messages.pop(0)

        self.messages.extend(messages)

        if len(self.messages) > self.k:
            old_messages = self.messages[:-self.k]
            self.messages = self.messages[-self.k:]

        if not old_messages:
            return

        summary_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "Given the existing conversation summary and the new messages, "
                "generate a new summary of the conversation while keeping important information."
            ),
            HumanMessagePromptTemplate.from_template(
                "Existing conversation summary:\n{existing_summary}\n\n"
                "New messages:\n{old_messages}"
            )
        ])

        # Stringify old messages
        formatted_old = "\n".join(f"{m.type.title()}: {m.content}" for m in old_messages)
        formatted_summary = existing_summary.content if existing_summary else ""

        new_summary = self.llm.invoke(
            summary_prompt.format_messages(
                existing_summary=formatted_summary,
                old_messages=formatted_old
            )
        )

        self.messages.insert(0, SystemMessage(content=new_summary.content))

    def clear(self) -> None:
        self.messages = []

    def get_summary_text(self) -> str:
        if self.messages and isinstance(self.messages[0], SystemMessage):
            return self.messages[0].content
        return ""

    def get_formatted_memory(self) -> str:
        """Returns the last k raw messages followed by summarized history."""
        summary = ""
        history = []

        for msg in self.messages:
            if isinstance(msg, SystemMessage):
                summary = msg.content
            else:
                role = "User" if isinstance(msg, HumanMessage) else "Assistant"
                history.append(f"{role}: {msg.content}")

        full_context = "\n".join(history)

        if summary:
            return f"{full_context}\n\n--- Summary of earlier conversation ---\n{summary}"
        else:
            return full_context