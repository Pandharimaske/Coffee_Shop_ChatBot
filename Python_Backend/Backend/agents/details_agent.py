from langchain_core.messages import ToolMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from Backend.prompts.details_prompt import details_prompt
from Backend.Tools.about_us import about_us_tool
from Backend.Tools.availability import check_availability_tool
from Backend.Tools.retriever_tool import rag_tool
from Backend.Tools.get_price import get_price_tool
from Backend.utils.logger import logger
from Backend.utils.util import load_llm
from Backend.schemas.state_schema import DetailsAgentState

class DetailsAgent:
    def __init__(self):
        self.llm = load_llm()

        self.llm_with_tools = self.llm.bind_tools([
            rag_tool, about_us_tool, check_availability_tool, get_price_tool
        ])

        self.agent_graph = create_react_agent(
            self.llm_with_tools,
            [rag_tool, about_us_tool, check_availability_tool, get_price_tool],
            prompt=details_prompt
        )

    def get_response(self, user_input: str) -> DetailsAgentState:
        try:
            if not user_input or not user_input.strip():
                return {"response_message": "You didn't say anything. Can I help with something?"}

            logger.debug(f"Running DetailsAgent for input: {user_input}")
            
            # Run agent with invoke and capture full message history
            result = self.agent_graph.invoke({"messages": [{"role": "user", "content": user_input}]})

            return {"response_message": result}


        except Exception as e:
            import traceback
            logger.error("Error in DetailsAgent:\n" + traceback.format_exc())
            return {"response_message": "Something went wrong. Please try again later."}

    def __call__(self, user_input: str) -> DetailsAgentState:
        return self.get_response(user_input)