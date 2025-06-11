import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableSequence  # keep for compatibility if needed
from Backend.pydantic_schemas.agents_schemas import GuardDecision
from Backend.prompts.gaurd_prompt import guard_prompt
from Backend.utils.logger import logger

load_dotenv()

class GuardAgent:
    """GuardAgent checks whether a user's query is within the allowed domain for a coffee shop assistant."""

    def __init__(self):
        llm = ChatGroq(
            model_name=os.getenv("GROQ_MODEL_NAME"),
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        # Setup chain with prompt and structured output
        self.chain = guard_prompt | llm.with_structured_output(GuardDecision)
        logger.info("GuardAgent initialized")
        logger.debug("GuardAgent chain is ready for evaluation.")

    def get_response(self, user_input: str) -> dict:
        """
        Evaluates the user's input and returns a structured decision with reasoning
        and a response message based on domain relevance.
        """
        try:
            logger.debug(f"Invoking guard chain with input: {user_input}")
            if not user_input or not user_input.strip():
                logger.warning("Received empty or invalid input to GuardAgent.")
            result = self.chain.invoke({"input": user_input})
            logger.debug(f"Guard chain invoked successfully. Structured result: {result}")
            logger.info(f"Guard Decision: {result.decision}, Message: {result.message}")

            return {
                "role": "assistant",
                "content": result.message if result.message else "I understand. How can I help you with your order?",
                "agent": "guard_agent",
                "guard_output": {
                    "guard_decision": result.decision,
                    "chain_of_thought": result.chain_of_thought
                }
            }

        except Exception as e:
            import traceback
            logger.error("GuardAgent error:\n" + traceback.format_exc())
            return {
                "role": "assistant",
                "content": "Something went wrong. Can I help you with something else?",
                "agent": "guard_agent",
                "guard_output": {
                    "guard_decision": "not allowed",
                    "chain_of_thought": "Error during processing"
                }
            }

    def __call__(self, user_input: str) -> dict:
        return self.get_response(user_input)