from langchain.output_parsers import PydanticOutputParser
from Backend.utils.logger import logger
from Backend.utils.util import call_llm
from Backend.schemas.agents_schemas import AgentDecision
from Backend.prompts.classification_prompt import classification_prompt
from Backend.schemas.state_schema import ClassificationAgentState


class ClassificationAgent:
    """ClassificationAgent classifies the user input into coffee shop-related tasks."""

    def __init__(self):
        logger.info("ClassificationAgent initialized")

    def get_response(self, user_input: str, state: dict) -> ClassificationAgentState:
        """
        Classify user input to appropriate agent.
        
        Args:
            user_input: The user's query
            state: Current conversation state (includes order, chat_summary, etc.)
        """
        try:
            # Extract order status
            order = state.get("order", None)
            if order and isinstance(order, dict) and len(order.get("items", [])) > 0:
                order_status = f"Order exists with {len(order['items'])} items"
            else:
                order_status = "No order"
            
            # Extract context
            context = state.get("chat_summary", "")
            
            logger.debug(f"Classifying input: {user_input} | Order: {order_status}")
            
            # Invoke prompt with all required variables
            prompt = classification_prompt.invoke({
                "user_input": user_input,
                "order_status": order_status,
                "context": context
            })
            
            # Call LLM
            result = call_llm(prompt=prompt, schema=AgentDecision)
            logger.debug(f"Classification result: {result}")
            
            return {
                "target_agent": result.target_agent,
                "response_message": result.response_message or "",
            }

        except Exception as e:
            import traceback
            logger.error("ClassificationAgent error:\n" + traceback.format_exc())
            return {
                "target_agent": "details_agent",  # Safe fallback
                "response_message": "",
            }

    def __call__(self, user_input: str, state: dict) -> ClassificationAgentState:
        return self.get_response(user_input, state)