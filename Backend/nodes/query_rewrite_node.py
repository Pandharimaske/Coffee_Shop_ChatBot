from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from Backend.utils.util import load_llm
from Backend.graph.states import CoffeeAgentState


class QueryRewriterNode(Runnable):
    def __init__(self):
        self.llm = load_llm()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
You are a query rewriting assistant for a coffee shop chatbot.

Your job is to make the user input fully self-contained and explicit **only if necessary**.

You are given:
- chat_summary: a summary of the conversation so far (may be empty)
- user_memory: user's known preferences (may be missing or partial)
- state: the complete current conversation state (may contain useful info)
- user_input: the current input from the user

✅ Your responsibilities:
- Only rewrite the user_input **if** it contains ambiguous references like "it", "same as before", "make it my favourite", etc.
- If the input is already explicit and clear, return it as-is.
- If the input is completely unrelated or irrelevant, leave it unchanged.
- DO NOT assume any value is always present. Use only the information provided.

Respond with the rewritten query string ONLY — no explanation, no formatting, just the updated query.
"""),
            ("human", """
Chat Summary:
{chat_summary}

User Memory:
{user_memory}

State:
{state}

User Input:
{user_input}
""")
        ])
        self.chain = self.prompt | self.llm | StrOutputParser()

    def invoke(self, state: CoffeeAgentState, config=None) -> CoffeeAgentState:
        user_input = state["user_input"]
        chat_summary = state.get("chat_summary", "")
        user_memory = state.get("user_memory", None)

        # Invoke LLM to rewrite query
        rewritten = self.chain.invoke({
            "user_input": user_input,
            "chat_summary": chat_summary,
            "user_memory": user_memory.dict() if user_memory else {},
            "state": state.dict() if hasattr(state, "dict") else {}
        })

        state["user_input"] = rewritten.strip()
        print("Rewritten Query:\n" , state["user_input"])
        return state
