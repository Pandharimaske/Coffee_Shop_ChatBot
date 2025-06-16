import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from Backend.schemas.agents_schemas import GuardDecision
from Backend.prompts.gaurd_prompt import guard_prompt
from Backend.utils.logger import logger
from typing import TypedDict, Literal

load_dotenv()

class GuardAgentOutput(TypedDict):
    decision: Literal["allowed", "not allowed"]
    response_message: str
    chain_of_thought: str

class GuardAgent:
    """GuardAgent checks whether a user's query is within the allowed domain for a coffee shop assistant."""

    def __init__(self):
        llm = ChatGroq(
            model_name=os.getenv("GROQ_MODEL_NAME"),
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        self.chain = guard_prompt | llm.with_structured_output(GuardDecision)
        logger.info("GuardAgent initialized")

    def get_response(self, user_input: str) -> GuardAgentOutput:
        try:
            logger.debug(f"Invoking guard chain with input: {user_input}")
            if not user_input or not user_input.strip():
                logger.warning("Received empty or invalid input to GuardAgent.")

            result = self.chain.invoke({"user_input": user_input})
            logger.debug(f"Guard chain result: {result}")

            return {
                "decision": result.decision,
                "response_message": result.response_message or "I understand. How can I help you with your order?",
                "chain_of_thought": result.chain_of_thought
            }

        except Exception as e:
            import traceback
            logger.error("GuardAgent error:\n" + traceback.format_exc())
            return {
                "decision": "not allowed",
                "response_message": "Something went wrong. Can I help you with something else?",
                "chain_of_thought": "Error during processing"
            }

    def __call__(self, user_input: str) -> GuardAgentOutput:
        return self.get_response(user_input)