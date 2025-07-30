from Backend.schemas.agents_schemas import GuardDecision
from Backend.prompts.gaurd_prompt import guard_prompt
from Backend.utils.logger import logger
from Backend.utils.util import load_llm
from Backend.schemas.state_schema import GuardAgentState
from Backend.graph.states import CoffeeAgentState

class GuardAgent:
    """GuardAgent checks whether a user's query is within the allowed domain for a coffee shop assistant."""

    def __init__(self):
        llm = load_llm()

        self.chain = guard_prompt | llm.with_structured_output(GuardDecision)
        logger.info("GuardAgent initialized")

    def get_response(self, state:CoffeeAgentState) -> GuardAgentState:
        try:
            user_input = state["user_input"]
            logger.debug(f"Invoking guard chain with input: {user_input}")
            if not user_input or not user_input.strip():
                logger.warning("Received empty or invalid input to GuardAgent.")

            result = self.chain.invoke({"user_input": user_input , "state":state})
            logger.debug(f"Guard chain result: {result}")

            return {
                "decision": result.decision,
                "response_message": result.response_message or "I understand. How can I help you with your order?" , 
                "memory_node":result.memory_node or False
            }

        except Exception as e:
            import traceback
            logger.error("GuardAgent error:\n" + traceback.format_exc())
            return {
                "decision": "not allowed",
                "response_message": "Something went wrong. Can I help you with something else?",
            }

    def __call__(self, state:CoffeeAgentState) -> GuardAgentState:
        return self.get_response(state)