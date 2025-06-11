import pprint
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from Backend.prompts.details_prompt import details_prompt
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.prebuilt import create_react_agent
from Backend.Tools.detailsagents_tools.about_us import about_us_tool
from Backend.Tools.detailsagents_tools.availability import check_availability_tool
from Backend.Tools.detailsagents_tools.retriever_tool import rag_tool
from Backend.Tools.detailsagents_tools.get_price import get_price_tool
from langsmith import traceable  # <-- Import LangSmith traceable decorator 
from langchain_core.messages import ToolMessage, AIMessage

load_dotenv()


class DetailsAgent:
    def __init__(self):
        # Initialize LLM agent
        self.agent_llm = ChatGroq(
            model_name=os.getenv("GROQ_MODEL_NAME"),
            temperature=0.2,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        llm_with_tools = self.agent_llm.bind_tools([rag_tool, about_us_tool, check_availability_tool , get_price_tool])

        # Initialize LangGraph agent
        self.agent_graph = create_react_agent(
            llm_with_tools,
            [rag_tool, about_us_tool, check_availability_tool , get_price_tool],
            prompt=details_prompt
        )

    @traceable(name="DetailsAgent Run")  # <-- Add traceable decorator here
    def get_response(self, user_input: str) -> dict:
        # Stream the agent graph and collect the last step
        stream = self.agent_graph.stream({"messages": [{"role": "user", "content": user_input}]})

        response = None  # Initialize
        for step in stream:
            if isinstance(step, (ToolMessage, AIMessage)):
                print("\n==== New step ====")
                pprint.pprint(step)
            response = step  # Save the last step (final AIMessage)

        return self.postprocess(response)

    def postprocess(self, output):
        return {
            "role": "assistant",
            "content": output.content if hasattr(output, "content") else str(output),
            "agent": "details_agent"
        }