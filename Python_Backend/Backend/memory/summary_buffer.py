from typing import List
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from Backend.utils.util import load_llm


class ConversationSummaryMemory(BaseModel):
    summary: str = ""
    llm = load_llm()

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Summarize the new messages along with existing summary and update internal state."""
        if not messages:
            return

        summary_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are an AI summarizer. Given the previous summary and new conversation messages, "
                "generate an updated summary that captures all important details without redundancy."
            ),
            HumanMessagePromptTemplate.from_template(
                "Previous summary:\n{existing_summary}\n\nNew messages:\n{new_messages}"
            )
        ])

        formatted_messages = "\n".join(
            f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
            for m in messages if isinstance(m, (HumanMessage, AIMessage))
        )

        # Format and invoke the prompt
        formatted = summary_prompt.format_messages(
            existing_summary=self.summary,
            new_messages=formatted_messages
        )

        new_summary_msg = self.llm.invoke(formatted)
        self.summary = new_summary_msg.content

    def clear(self) -> None:
        self.summary = ""

    def get_summary_text(self) -> str:
        return self.summary

    def get_formatted_memory(self) -> str:
        return f"--- Summary of the conversation ---\n{self.summary}" if self.summary else ""