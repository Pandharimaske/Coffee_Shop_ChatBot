import pprint
from langchain_core.messages import ToolMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from Backend.prompts.details_prompt import details_prompt
from Backend.Tools.detailsagents_tools.about_us import about_us_tool
from Backend.Tools.detailsagents_tools.availability import check_availability_tool
from Backend.Tools.detailsagents_tools.retriever_tool import rag_tool
from Backend.Tools.detailsagents_tools.get_price import get_price_tool
from Backend.utils.logger import logger
from Backend.utils.util import llm
from Backend.schemas.state_schema import DetailsAgentState

class DetailsAgent:
    def __init__(self):
        self.llm = llm

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

            print("\n==== Full message trace ====")
            for msg in result["messages"]:
                pprint.pprint(msg)

            # Extract final AI response
            last_msg = next(
                (m for m in reversed(result["messages"]) if isinstance(m, AIMessage) and m.content.strip()),
                None
            )

            if last_msg:
                return {"response_message": last_msg.content}
            else:
                logger.warning("No final AIMessage with content found.")
                return {"response_message": "I wasn't able to find a helpful answer for that."}

        except Exception as e:
            import traceback
            logger.error("Error in DetailsAgent:\n" + traceback.format_exc())
            return {"response_message": "Something went wrong. Please try again later."}
        #     stream = self.agent_graph.stream({"messages": [{"role": "user", "content": user_input}]})

        #     final_message = None

        #     for step in stream:
        #         print("\n==== New step ====")
        #         pprint.pprint(step)

        #         if isinstance(step, (ToolMessage, AIMessage)):
        #             final_message = step  # Save last AIMessage for return

        #     if isinstance(final_message, AIMessage):
        #         return {"response_message":final_message.content}

        #     logger.warning("No AIMessage found in response stream.")
        #     return {"response_message":"I couldn't find a clear answer for that."}

        # except Exception as e:
        #     import traceback
        #     logger.error("DetailsAgent error:\n" + traceback.format_exc())
        #     return {"response_message":"Something went wrong while answering your question."}

    def __call__(self, user_input: str) -> DetailsAgentState:
        return self.get_response(user_input)